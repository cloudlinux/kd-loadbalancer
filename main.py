import asyncio
import json
import logging
import os
from json.decoder import JSONDecodeError

import aiohttp
import requests
import yaml
from jinja2 import Template
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from k8s_client import Ingress, ReplicationController, Service, Secret

logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s] %(message)s',
    level=logging.DEBUG,
    filename=u'working.log')

logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def create_base_rc():
    rc = ReplicationController(namespace='default', config=config['apiserver'])
    for item in (
        ('base', 'nginx-controller', 'nginx-ingress-rc.yaml'),
        ('base', 'certbot', 'certbot-rc.yaml')
    ):
        with open(os.path.join(*item), 'r') as f:
            rc.create(yaml.load(f.read()))


def create_base_svc():
    svc = Service(namespace='default', config=config['apiserver'])
    for item in (
        ('base', 'certbot', 'certbot-svc.yaml'),
    ):
        with open(os.path.join(*item), 'r') as f:
            svc.create(yaml.load(f.read()))


def create_main_rc_and_svc(data):
    for name in data['services']:
        rc = ReplicationController(namespace='default',
                                   config=config['apiserver'])
        with open(os.path.join('templates', 'rc-rule.yaml.j2'), 'r') as f:
            yaml_data = Template(f.read()).render({'name': name})
            rc.create(yaml.load(yaml_data))

        svc = Service(namespace='default', config=config['apiserver'])
        with open(os.path.join('templates', 'svc-rule.yaml.j2'), 'r') as f:
            yaml_data = Template(f.read()).render({'name': name})
            svc.create(yaml.load(yaml_data))


def main(config):
    # Create rc: nginx-controller and certbot
    create_base_rc()

    # Create certbot service
    create_base_svc()

    # Create for fixtures
    with open(config['fixtures'], 'r') as f:
        data = json.loads(f.read())

    # Create rc and service for endpoint, for example owncloud
    create_main_rc_and_svc(data)

    input("Please enter when certbot rc will be running")

    # Create ingress rules, TLS certs and secrets
    create_ingress(data['ingress-rules'])


# Create ingress rules
def create_ingress_rule(name, host, service_name):
    ing = Ingress(namespace='default', config=config['apiserver'])
    for item in (
        ('templates', 'ingress-rule.yaml.j2'),
    ):
        with open(os.path.join(*item), 'r') as f:
            yaml_data = Template(f.read()).render({
                'name': name,
                'host': host,
                'service_name': service_name
            })
            ing.create(yaml.load(yaml_data))


def replace_ingress_rule(name, host, service_name):
    ing = Ingress(namespace='default', config=config['apiserver'])
    for item in (
        ('templates', 'ingress-rule.yaml.j2'),
    ):
        with open(os.path.join(*item), 'r') as f:
            yaml_data = Template(f.read()).render({
                'name': name,
                'host': host,
                'service_name': service_name
            })
            ing.replace('{}-ingress'.format(name), yaml.load(yaml_data))


# Create secrets
def create_secret(name, cert, private_key):
    ing = Secret(namespace='default', config=config['apiserver'])
    for item in (
        ('templates', 'secret-rule.yaml.j2'),
    ):
        with open(os.path.join(*item), 'r') as f:
            yaml_data = Template(f.read()).render({
                'cert': cert,
                'private_key': private_key,
                'name': name
            })
            ing.create(yaml.load(yaml_data))


async def fetch(session, url, data, seconds):
    await asyncio.sleep(seconds)
    logger.debug('Run generating cert via {} after {} sec'.format(
        url, seconds))

    async with session.post(
        url,
        data=json.dumps(data),
        headers={
            'Content-type': 'application/json'
        }
    ) as response:
        response = await response.text()
        return response


def create_ingress(ingress_rules):
    loop = asyncio.get_event_loop()

    with aiohttp.ClientSession(loop=loop) as session:
        total = len(ingress_rules)
        # 2 sec delay between tasks  - experimental
        coefficient = 2 * total

        additional_params = []
        if config['certbot']['staging']:
            additional_params.append('--staging')

        tasks = []
        for i, (name, host, service_name) in enumerate(ingress_rules):
            create_ingress_rule(name, host, service_name)

            tasks.append(asyncio.ensure_future(fetch(
                session, 'http://{}/.certs/'.format(host), {
                    'domains': [host],
                    'email': config['certbot']['email'],
                    'certbot-additional-params': additional_params
                }, i * 1.0 / total * coefficient
            )))

        loop.run_until_complete(
            asyncio.wait(tasks)
        )
        for i, task in enumerate(tasks):
            name, host, service_name = ingress_rules[i]
            try:
                result = json.loads(task.result())
            except JSONDecodeError:
                logger.error(task.result())
                raise SystemExit("Certificates not generated")
            create_secret(
                name,
                cert=result['cert'],
                private_key=result['private_key']
            )
            replace_ingress_rule(name, host, service_name)


if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.load(f.read())
    main(config)

import logging

import CloudFlare

logger = logging.getLogger(__name__)


def create_or_update_ip(domain, new_ips, **kwargs):
    """
    Create or update DNS record with type A for IP addresses of load
    balancer

    :param domain: New subdomain name in existing zone
    :param new_ips: IP addresses of load balancer
    :param kwargs: additional params such as email and
        token and certtoken for access to Cloudflare API
    :return:
    """
    kwargs.pop('name')
    cf = CloudFlare.CloudFlare(**kwargs)
    for zone in cf.zones.get():

        if zone['name'] in domain:
            for dns_record in cf.zones.dns_records.get(zone['id']):
                if domain == dns_record['name']:
                    # cloudflare can attach only one ip address
                    if dns_record['content'] not in new_ips:
                        new_ip = new_ips[0]
                        data = {
                            # getting first ip
                            'content': new_ip,
                            # https://github.com/danni/python-cloudflare/blob/python3ify/examples/example-create-zone-and-populate.py#L59
                            'type': dns_record['type'],
                            'name': dns_record['name']
                        }
                        cf.zones.dns_records.put(
                            zone['id'],
                            dns_record['id'],
                            data=data)
                        logger.debug(
                            'Replace record in zone "{zone}" with '
                            'domain "{domain}" '
                            'and ip "{ips}"'.format(
                                zone=zone['name'], domain=domain, ips=new_ip
                            ))

                    else:
                        logger.debug(
                            'Domain "{domain}" with '
                            'ip "{ips}" in zone "{zone}" '
                            'already exists'.format(
                                zone=zone['name'], domain=domain, ips=new_ips
                            ))

                    break

            else:
                # cloudflare can attach only one ip address
                new_ip = new_ips[0]
                data = {
                    # getting first ip
                    'content': new_ip,
                    'type': 'A',
                    'name': domain
                }
                cf.zones.dns_records.post(zone['id'], data=data)
                logger.debug(
                    'Create new record in zone "{zone}" with '
                    '"{domain}" '
                    'and ip "{ips}"'.format(
                        zone=zone['name'], domain=domain, ips=new_ips
                    ))

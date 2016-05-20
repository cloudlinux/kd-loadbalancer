import json
import logging
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


class KubernetesClient(object):
    def __init__(self, config):
        self.server = config.get('server', 'http://localhost:8080/')

    def _request(self, method, url_path, data):
        url = urljoin(self.server, url_path)

        if method == 'GET':
            response = requests.request(
                method, url, params=data, headers={
                    'Content-Type': 'application/json'
                })
        else:
            response = requests.request(
                method, url, data=data, headers={
                    'Content-Type': 'application/json'
                })

        result = json.loads(response.content.decode('utf-8'))

        if response.status_code not in [200, 201]:
            logger.debug('  {status}: "{message}"'.format(**result))
        else:
            logger.debug('  Success')

        return result


class KubernetesOperations(KubernetesClient):
    entity = None
    path = '/api/v1/namespaces/{namespace}/{entity}'

    def __init__(self, namespace, *args, **kwargs):
        super(KubernetesOperations, self).__init__(*args, **kwargs)
        self.namespace = namespace

    def list(self, *args, **kwargs):
        return

    def create(self, data):
        path = self.path.format(
            **{'namespace': self.namespace,
               'entity': self.entity}
        )

        logger.debug('{} {}: "{name}"'.format(
            'POST',
            self.__class__.__name__,
            **data.get('metadata', {'name': None})
        ))

        return self._request('POST', path, json.dumps(data))

    def read(self):
        pass

    def replace(self, name, data):
        path = self.path.format(
            **{'namespace': self.namespace,
               'entity': self.entity}
        )

        logger.debug('{} {}: "{name}"'.format(
            'PUT',
            self.__class__.__name__,
            **data.get('metadata', {'name': None})
        ))
        return self._request(
            'PUT',
            urljoin(path, name),
            json.dumps(data))

    def delete(self):
        pass

    def partially_update(self):
        pass


class ReplicationController(KubernetesOperations):
    entity = 'replicationcontrollers'


class Service(KubernetesOperations):
    entity = 'services'


class Secret(KubernetesOperations):
    entity = 'secrets'


class Namespace(KubernetesClient):
    def read(self):
        pass

    def replace(self):
        pass

    def delete(self):
        pass

    def partially_update(self):
        pass


class Pod(KubernetesOperations):
    path = '/api/v1/namespaces/{namespace}/pods'

    def list(self, label_selector=None, field_selector=None):
        path = self.path.format(
            **{'namespace': self.namespace}
        )
        logger.debug('{} {}: "{}"'.format(
            'GET',
            self.__class__.__name__,
            'list')
        )

        return self._request('GET', path, {
            'labelSelector': label_selector,
            'fieldSelector': field_selector,
        })


class ExecPod(KubernetesOperations):
    path = '/api/v1/namespaces/{namespace}/pods/{name}/exec'

    def __init__(self, pod, *args, **kwargs):
        super(ExecPod, self).__init__(*args, **kwargs)
        self.pod = pod

    def execute(self, command=None):
        path = self.path.format(
            **{'namespace': self.namespace,
               'name': self.pod}
        )
        return self._request('GET', path, {
            'command': command
        })


# Extensions:

class Ingress(KubernetesOperations):
    entity = 'ingresses/'
    path = '/apis/extensions/v1beta1/namespaces/{namespace}/{entity}'

import json
import random
import string

import sys


def create_fixtures(domain, n=1):
    name = ''.join(random.choice(string.ascii_lowercase)
                   for _ in range(3))
    service = '{}-owncloud'.format(name)
    data = {'services': [service], 'ingress-rules': [
        [
            "{}-{}".format(name, i),
            "{}-{}.{}".format(name, i, domain),
            service
        ]
        for i in range(int(n))]}

    with open('fixtures.json', 'w') as f:
        f.write(
            json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        )


if __name__ == '__main__':
    create_fixtures(sys.argv[1], sys.argv[2])

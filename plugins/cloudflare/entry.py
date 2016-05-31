import logging

import CloudFlare

logger = logging.getLogger(__name__)


def create_or_update_ip(domain, new_ips, **kwargs):
    """
    Create or update DNS record with type A for IP addresses of load
    balancer

    :param str domain: New subdomain name in existing zone
    :param list new_ips: IP addresses of load balancer
    :param dict kwargs: additional params such as email and
        token and certtoken for access to Cloudflare API
    :return:
    """
    kwargs.pop('name')
    cf = CloudFlare.CloudFlare(**kwargs)
    for zone in cf.zones.get():

        if zone['name'] in domain:
            for dns_record in cf.zones.dns_records.get(zone['id']):
                if domain == dns_record['name']:

                    if dns_record['content'] not in new_ips:
                        # cloudflare can assign only one ip address
                        # here you can use roundrobin for many ip addresses
                        new_ip = new_ips[0]
                        data = {
                            'content': new_ip,
                            # Requires other fields
                            # https://github.com/danni/python-cloudflare/blob
                            # /python3ify/examples
                            # /example-create-zone-and-populate.py#L59

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
                # cloudflare can assign only one ip address
                # here you can use roundrobin for many ip addresses
                new_ip = new_ips[0]
                data = {
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
            break
    else:
        raise ValueError("Zone for domain {} not found. "
                         "Need to configure the zone".format(domain))

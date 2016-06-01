import logging

from .dnsonly_client import API

logger = logging.getLogger(__name__)


def delete_a_record(domain, **kwargs):
    """
    Delete A record to domain

    :param domain: domain which will have been deleted
    :param dict kwargs: additional params such as email and
        token and certtoken for access to Cloudflare API
    :return: None
    """
    kwargs.pop('name')
    api = API(**kwargs)
    for zone in api.zones():

        if zone.name in domain:
            for dns_record in zone.records():
                # dns record without end point
                if dns_record.type == 'A' and domain == dns_record.name[:-1]:
                    dns_record.delete()


def create_or_update_a_record(domain, new_ips, **kwargs):
    """
    Create or update A record for IP addresses of load
    balancer

    :param str domain: New subdomain name in existing zone
    :param list new_ips: IP addresses of load balancer
    :param dict kwargs: additional params such as token for access WHM API
    :return:
    """

    kwargs.pop('name')
    api = API(**kwargs)
    for zone in api.zones():

        if zone.name in domain:
            for dns_record in zone.records():
                # dns record without end point
                if dns_record.type == 'A' and domain == dns_record.name[:-1]:
                    if dns_record.address not in new_ips:
                        # dnsonly can assign only one ip address
                        # here you can use roundrobin for many ip addresses
                        new_ip = new_ips[0]

                        dns_record.address = new_ip
                        dns_record.edit()

                        logger.debug(
                            'Replace record in zone "{zone}" with '
                            'domain "{domain}" '
                            'and ip "{ips}"'.format(
                                zone=zone.name, domain=domain, ips=new_ip
                            ))

                    else:
                        logger.debug(
                            'Domain "{domain}" with '
                            'ip "{ips}" in zone "{zone}" '
                            'already exists'.format(
                                zone=zone.name, domain=domain, ips=new_ips
                            ))

                    break

            else:
                # dnsonly can assign only one ip address
                # here you can use roundrobin for many ip addresses
                new_ip = new_ips[0]

                zone.add_a_record(domain, new_ip)
                logger.debug(
                    'Create new record in zone "{zone}" with '
                    '"{domain}" '
                    'and ip "{ips}"'.format(
                        zone=zone.name, domain=domain, ips=new_ips
                    ))
            break
    else:
        raise ValueError("Zone for domain {} not found. "
                         "Need to configure the zone".format(domain))

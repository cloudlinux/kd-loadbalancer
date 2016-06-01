import logging

import route53

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
    conn = route53.connect(
        aws_access_key_id=kwargs['aws-access-key-id'],
        aws_secret_access_key=kwargs['aws-secret-access-key'])

    for zone in conn.list_hosted_zones():
        # [:-1] without end point
        if zone.name[:-1] in domain:
            for dns_record in zone.record_sets:

                if domain == dns_record.name[:-1]:
                    dns_record.delete()


def create_or_update_a_record(domain, new_ips, **kwargs):
    """
    Create or update A record for IP addresses of load
    balancer

    :param str domain: New subdomain name in existing zone
    :param list new_ips: IP addresses of load balancer
    :param dict kwargs: additional params such as aws-access-key-id and
        aws-secret-access-key for access to AWS ROUTE 53
    :return:
    """
    assert isinstance(new_ips, list)
    conn = route53.connect(
        aws_access_key_id=kwargs['aws-access-key-id'],
        aws_secret_access_key=kwargs['aws-secret-access-key'])

    for zone in conn.list_hosted_zones():
        # [:-1] without end point
        if zone.name[:-1] in domain:
            for dns_record in zone.record_sets:
                # [:-1] without end point
                if domain == dns_record.name[:-1]:
                    if set(new_ips) != set(dns_record.records):
                        dns_record.records = new_ips
                        dns_record.save()

                        logger.debug(
                            'Replace record in zone "{zone}" with '
                            'domain "{domain}" '
                            'and ip "{ips}"'.format(
                                zone=zone.name, domain=domain, ips=new_ips
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
                zone.create_a_record(domain, new_ips)
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


## DNS support

After creating pod of load balancer you can bind new subdomain name 
and new IP address of load balancer in the DNS server.

Out of the box you can use adapters for DNS servers:

* cloudflare
* aws route 53
* cPanel DNSONLY

you should have existing zone in your DNS server 
and configured name server (NS) for your domain.


## Configuring DNS support

* CloudFlare

    Related part of `config.yaml`:

    ```
    plugins:
      dns:
        name: cloudflare
        
        # Your email from settings cloudflare account
        email: yourmail@example.com
        
        # Your token from settings cloudflare account 
        token: #########################
        
        # Your token from settings cloudflare account 
        certtoken: v1.0-##################################################
    
    ```

* AWS Route 53

    Related part of `config.yaml`:

    ```
    plugins:
      dns:
        name: aws_route53
        
        # Your AWS access key id from AWS Identity and Access Management
        aws-access-key-id: ###########
        
        # Your AWS secret access key from AWS Identity and Access Management
        aws-secret-access-key: ############################################
    
    ```

* cPanel DNSONLY

    Related part of `config.yaml`:

    ```
    plugins:
      dns:
        name: cpanel_dnsonly
        
        # Your WHM DNSONLY host
        host: https://95.164.68.73:2087
        
        # User for access to WHM DNSONLY via API
        user: root
        
        # Access key for user
        token: ############################################
    
    ```

## How to implement own DNS plugin

It should be python package in the plugins folder with three files:

* `__init__.py` - required
* `entry.py` - required
* `REQUIREMENTS` - required if you have additional dependencies. Dependencies 
should be installed manually.

`entry.py` also should contains `create_or_update_ip` function for create or 
update existing DNS records with A type. Params `create_or_update_ip`:

* *domain* - type `str` - new subdomain name in the existing zone
* *new_ips* - type `list` - list of IP-addresses for load balancer
* *kwargs* - type `dict` - key-word arguments, additional params from config file, like credentional for access to
API

All examples you can take a look in `aws_route53`, `cloudflare` 
or `cpanel_dnsonly` plugins.
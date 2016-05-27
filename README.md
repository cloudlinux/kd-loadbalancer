# owncloud + trust TLS cert from letsencrypt 

## Prerequisites
* Kubernetes 1.2 or higher (TSL support for Ingress has been added in 1.2)
* k8s addon DNS with service name "kube-dns"
* Python 3.5

## Installation

```
$ mkvirtualenv -p /usr/local/bin/python3.5 test-ingress
$ git clone https://github.com/prefer/test-ingress.git
$ cd test-ingress/
$ pip install -R REQUIREMENTS
```

### Generating fixtures

```
(test-ingress) $ python3.5 generate_fixtures.py c cl-owncloud.pro 5
```
Where:
* `c` - prefix for subdomain
* `cl-owncloud.pro` - base domain
* `5` - amount sub-domains for generating

After execution command you will see result in the `fixtures.json`

### Change config and templates

* Create config based on the config.yaml.template
* Change templates (base/, templates/) if necessary

### Supporting dynamic add dns records

Supported:

* amazon route53
* cloudflare

**Important!** Zone for domains should be created.

## Running 

```
(test-ingress) $ python3.5 main.py
```

You should see something like:
```
Create ReplicationController: "nginx-ingress-rc"
  Failure: "replicationcontrollers "nginx-ingress-rc" already exists"
Create ReplicationController: "certbot-rc"
  Failure: "replicationcontrollers "certbot-rc" already exists"
Create Service: "certbot-svc"
  Failure: "services "certbot-svc" already exists"
Create ReplicationController: "c-8318aed6-owncloud-rc"
  Success
Create Service: "c-8318aed6-owncloud-svc"
Please enter when certbot rc will be running  Success

Using selector: KqueueSelector
Create Ingress: "c-8318aed6-0-ingress"
  Success
Create Ingress: "c-8318aed6-1-ingress"
  Success
Create Ingress: "c-8318aed6-2-ingress"
  Success
Create Ingress: "c-8318aed6-3-ingress"
  Success
Create Ingress: "c-8318aed6-4-ingress"
  Success
run generating cert via http://c-8318aed6-0.cl-owncloud.pro/.certs/ after 0.0 sec
run generating cert via http://c-8318aed6-1.cl-owncloud.pro/.certs/ after 2.0 sec
run generating cert via http://c-8318aed6-2.cl-owncloud.pro/.certs/ after 4.0 sec
run generating cert via http://c-8318aed6-3.cl-owncloud.pro/.certs/ after 6.0 sec
run generating cert via http://c-8318aed6-4.cl-owncloud.pro/.certs/ after 8.0 sec
Create Secret: "c-8318aed6-0-secret"
  Success
Replace Ingress: "c-8318aed6-0-ingress"
  Success
Create Secret: "c-8318aed6-1-secret"
  Success
Replace Ingress: "c-8318aed6-1-ingress"
  Success
Create Secret: "c-8318aed6-2-secret"
  Success
Replace Ingress: "c-8318aed6-2-ingress"
  Success
Create Secret: "c-8318aed6-3-secret"
  Success
Replace Ingress: "c-8318aed6-3-ingress"
  Success
Create Secret: "c-8318aed6-4-secret"
  Success
Replace Ingress: "c-8318aed6-4-ingress"
  Success
```

## Results

After successful result without errors you could go to new subdomains:

* http://c-8318aed6-0.cl-owncloud.pro/
* http://c-8318aed6-1.cl-owncloud.pro/
* http://c-8318aed6-2.cl-owncloud.pro/
* http://c-8318aed6-3.cl-owncloud.pro/
* http://c-8318aed6-4.cl-owncloud.pro/

Redirect to https will be automatically.
For a while as backend used only one owncloud pod for all domain.
If you use `staging: true` in the config you get untrusted TLS cert for domain.


## Troubleshooting

### Not working dns
Dns on the pods from replicaset "certbot-rc" should be work. If you have this problem you can add nameserver manually:
```
$ kubectl exec certbot-rc-ucc2x -it bash
$ root@certbot-rc-as9bv:/opt/certbot# cat >> /etc/resolv.conf <<EOF
nameserver 8.8.8.8
EOF
```

### Nginx time-out when certificate generating

If you see next one:
```
DEBUG    [2016-05-23 13:59:12,054] run generating cert via http://c-c33c80c1-0.cl-owncloud.pro/.certs/ after 0.0 sec
ERROR    [2016-05-23 14:00:12,449] <html>
<head><title>504 Gateway Time-out</title></head>
<body bgcolor="white">
<center><h1>504 Gateway Time-out</h1></center>
<hr><center>nginx/1.9.15</center>
</body>
</html>
```

You could add timeout to nginx pod:
```
$ kubectl exec nginx-ingress-rc-jyz5t -it bash
root@nginx-ingress-rc-jyz5t:/# cat >> /etc/nginx/conf.d/timeout.conf<<EOF
proxy_connect_timeout       600;
proxy_send_timeout          600;
proxy_read_timeout          600;
send_timeout                600;
EOF
root@nginx-ingress-rc-jyz5t:/# service nginx reload 
```

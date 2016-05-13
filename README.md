# Owncloud with ingress k8s

## Prerequisites

* Kubernetes 1.2 (TSL support for Ingress has been added in 1.2)
* k8s addon DNS with service name "kube-dns"

## Running

1. Create services and replication controllers:

  ```
  $ kubectl create -f igor-owncloud-rc.yaml
  $ kubectl create -f igor-owncloud-svc.yaml
  $ kubectl create -f nikolay-owncloud-rc.yaml
  $ kubectl create -f nikolay-owncloud-svc.yaml
  ```
1. Create a Secret with an trusted SSL certificate and a key:
  
  First you should generate SSL by [letsencrypt.org](https://letsencrypt.org/), for example:
  ```
  $ git clone https://github.com/letsencrypt/letsencrypt
  $ cd letsencrypt
  $ ./letsencrypt-auto --help
  $ ./letsencrypt-auto certonly --standalone --email admin@example.com -d nikolay.example.com
  $ ./letsencrypt-auto certonly --standalone --email admin@example.com -d igor.example.com
  ```
  In the examples I uses my domain name `diveinto.ru`, you should use own domain name, letsencrypt doesn't work if domain name will not be linked with your ip address.
  You can find certificates in the folder - ```/etc/letsencrypt/live/nikolay.example.com``` or ```/etc/letsencrypt/live/igor.example.com```

  Second you should create secrets:
  ```
  $ kubectl create secret generic nikolay-owncloud-secret --from-file=tls.key=nikolay.priv.pem --from-file=tls.crt=nikolay.cert.pem
  $ kubectl create secret generic igor-owncloud-secret --from-file=tls.key=igor.priv.pem --from-file=tls.crt=igor.cert.pem
  ```
  ```*.priv.pem, *.cert.pem``` - files after generate certs for own domain by [letsencrypt.org](https://letsencrypt.org/).

1. Create Ingress Resource:
  ```
  $ kubectl create -f nikolay-owncloud-ingress.yaml
  $ kubectl create -f igor-owncloud-ingress.yaml
  ```

1. Create either NGINX Ingress Controller:
  ```
  $ kubectl create -f nginx-ingress-rc.yaml
  ```

1. The Controller container exposes ports 80, 443
on the host it runs. Make sure to add a firewall to allow incoming traffic
on this ports.

1. Find out the IP address of the node of the controller:
  ```
  $ LBNODE=$(kubectl get po -l app=nginx-ingress -o go-template --template '{{range .items}}{{.spec.nodeName}}{{end}}')
  $ LBIP=$(kubectl get no $LBNODE -o go-template --template '{{range $i, $n := .status.addresses}}{{if eq $n.type "InternalIP"}}{{$n.address}}{{end}}{{end}}')
  $ echo $LBIP
    194.44.0.62
  ```

  ```
  $ kubectl get node node1 -o yaml | grep -B1 InternalIP
    - address: 194.44.0.62
      type: InternalIP
  ```


1. We'll use ```curl```'s --insecure to turn off certificate verification of our self-signed
certificate and --resolve option to set the Host header of a request with ```cl-owncloud.com```
  To get one app owncloud:
  ```
  $ curl --resolve igor.cl-owncloud.com:443:$LBIP https://igor.cl-owncloud.com --insecure
  <!DOCTYPE html>
  <html>
    ...
  ```
  To get next app owncloud:
  ```
  $ curl --resolve nikolay.cl-owncloud.com:443:$LBIP https://nikolay.cl-owncloud.com --insecure
  <!DOCTYPE html>
  <html>
    ...
  ```

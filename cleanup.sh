#!/usr/bin/env bash

kubectl delete rc -l type=letsencrypt
kubectl delete svc -l type=letsencrypt
kubectl delete secrets --all
kubectl delete ing --all
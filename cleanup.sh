#!/usr/bin/env bash

#kubectl delete rc certbot-rc
kubectl delete secrets --all
kubectl delete ing --all
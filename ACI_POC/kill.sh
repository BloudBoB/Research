#!/bin/bash
while true; do docker kill $(docker ps -a -q --filter ancestor=k8s-gcrio.azureedge.net/hyperkube-amd64:v1.8.4 --format="{{.ID}}") ; done
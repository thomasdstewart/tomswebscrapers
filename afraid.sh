#!/bin/bash -eux

#wget -O afraid1.html http://freedns.afraid.org/domain/registry/

for n in $(seq 2 841); do
        echo wget -O afraid$n.html http://freedns.afraid.org/domain/registry/?page=$n
        sleep 1
done

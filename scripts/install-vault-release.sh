#!/bin/bash
set -eux

DEFAULT_VAULT_VERSION=0.11.1
VAULT_VERSION=${1:-$DEFAULT_VAULT_VERSION}

mkdir -p $HOME/bin

cd /tmp

curl -sOL https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip
unzip vault_${VAULT_VERSION}_linux_amd64.zip
mv vault $HOME/bin

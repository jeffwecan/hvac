#!/bin/bash
set -eux

DEFAULT_VAULT_VERSION=0.11.1
VAULT_VERSION=${1:-$DEFAULT_VAULT_VERSION}

if [[ "$VAULT_VERSION" == "head" ]]; then
    source install-vault-head.sh
else
    source install-vault-release.sh "$VAULT_VERSION"
fi

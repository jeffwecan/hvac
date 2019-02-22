backend "inmem" {
}

listener "tcp" {
  tls_disable = true
}

disable_mlock = true

default_lease_ttl = "768h"
max_lease_ttl = "768h"

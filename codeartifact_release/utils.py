import sys
from os import environ

DOMAIN = 'CODEARTIFACT_DOMAIN'
DOMAIN_OWNER = 'CODEARTIFACT_DOMAIN_OWNER'
REPOSITORY = 'CODEARTIFACT_REPOSITORY'
config_keys = [DOMAIN, DOMAIN_OWNER, REPOSITORY]


def get_config() -> dict:
    config = {}
    for config_key in config_keys:
        if config_key in environ:
            config[config_key] = environ.get(config_key)
        else:
            sys.exit(f'Environment variable {config_key} is not set, exiting')
    return config

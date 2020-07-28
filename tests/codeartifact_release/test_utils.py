from os import environ

import codeartifact_release.utils as utils

environ['CODEARTIFACT_DOMAIN'] = 'test'
environ['CODEARTIFACT_DOMAIN_OWNER'] = '123456789123'
environ['CODEARTIFACT_REPOSITORY'] = 'pypi'


def test_get_config():
    config = utils.get_config()
    assert config['CODEARTIFACT_DOMAIN'] == 'test'
    assert config['CODEARTIFACT_DOMAIN_OWNER'] == '123456789123'
    assert config['CODEARTIFACT_REPOSITORY'] == 'pypi'
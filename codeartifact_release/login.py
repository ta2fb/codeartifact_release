import logging
import subprocess

from codeartifact_release import utils


def main():
    config = utils.get_config()

    logging.info('Configuring pip for CodeArtifact and obtaining new credentials')
    subprocess.call(['aws', 'codeartifact', 'login', '--tool', 'pip',
                     '--repository', config[utils.REPOSITORY],
                     '--domain', config[utils.DOMAIN],
                     '--domain-owner', str(config[utils.DOMAIN_OWNER])])

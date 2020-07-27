import argparse
import logging
from os import chdir, environ, getcwd
from pathlib import Path
import re
import subprocess
import sys

# TODO: remove fourth version option
version_pattern = re.compile(r'^[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}(\.[0-9]{1,2})?$')
domain = 'CODEARTIFACT_DOMAIN'
domain_owner = 'CODEARTIFACT_DOMAIN_OWNER'
repository = 'CODEARTIFACT_REPOSITORY'
config_keys = [domain, domain_owner, repository]
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


def get_config() -> dict:
    config = {}
    for config_key in config_keys:
        if config_key in environ:
            config[config_key] = environ.get(config_key)
        else:
            sys.exit(f'Environment variable {config_key} is not set, exiting')
    return config


def version_type(arg_value: str):
    if not version_pattern.match(arg_value):
        raise argparse.ArgumentTypeError(f'Invalid version: {arg_value}, needs to be ##.##.##')
    return arg_value


def pad_version(version: str):
    version_split = version.split('.')
    if len(version_split) == 4:
        return version
    else:
        return f'{version}.0'


def version_compare(old_version: str, new_version: str) -> bool:
    # TODO: make this more efficient
    old_x, old_y, old_z, old_extra = list(map(int, pad_version(old_version).split('.')))
    new_x, new_y, new_z, new_extra = list(map(int, pad_version(new_version).split('.')))
    if old_x < new_x:
        return True
    elif old_x > new_x:
        return False
    else:
        if old_y < new_y:
            return True
        elif old_y > new_y:
            return False
        else:
            if old_z < new_z:
                return True
            elif old_z > new_z:
                return False
            else:
                if old_extra < new_extra:
                    return True
                elif old_extra > new_extra:
                    return False
                else:
                    return False


def get_stdout_as_str(process) -> str:
    return process.stdout.read().decode('utf-8').rstrip()


def check_release_command(process: int):
    if process == 0:
        logging.info('Release command successful, proceeding')
    else:
        sys.exit('Release command failed, exiting')


def run_release_command():
    process = subprocess.call(['tox',  '-e', 'release'])
    check_release_command(process)


def upload_to_codeartifact(version: str):
    logging.info('Building the distribution')
    subprocess.call(['python', 'setup.py', 'sdist'])
    logging.info('Uploading the tar.gz to CodeArtifact')
    subprocess.call(['twine', 'upload', '-r', 'codeartifact', f'dist/*{version}.tar.gz'])
    logging.info('Uploading the whl to CodeArtifact')
    subprocess.call(['twine', 'upload', '-r', 'codeartifact', f'dist/*{version}-*.whl'])


def main():
    config = get_config()

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', type=version_type, help='Version to release (format should be ##.##.##)')
    parser.add_argument('--package_dirs', type=str, help='(Optional) List package directories to loop over, '
                                                         'comma separated')
    args = parser.parse_args()
    package_dirs = args.package_dirs.split(',') if args.package_dirs else None

    root_dir = Path(getcwd()).resolve()

    p1 = subprocess.Popen(['git', 'describe', '--abbrev=0', '--tags'], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL)
    latest_tag = get_stdout_as_str(p1)
    if not version_pattern.match(latest_tag):
        latest_tag = '0.0.0'

    if version_compare(latest_tag, args.version):
        logging.info(f'The candidate release version {args.version} is greater than the previous tag {latest_tag}, '
                     'proceeding')
    else:
        sys.exit(f'The candidate release version {args.version} is not greater than the previous tag {latest_tag}, '
                 'exiting')

    p2 = subprocess.Popen(['git', 'diff-index', 'HEAD', '--'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if get_stdout_as_str(p2):
        sys.exit('There are uncommitted changes, exiting')
    else:
        logging.info('There are no uncommitted changes, proceeding')

    if package_dirs:
        for package_dir in package_dirs:
            logging.info(f'Running the tox release command for {package_dir}')
            chdir(root_dir / package_dir)
            logging.debug(f'cwd: {getcwd()}')
            run_release_command()
            chdir(root_dir)
            logging.debug(f'cwd: {getcwd()}')
    else:
        logging.info('Running the tox release command')
        run_release_command()

    logging.info(f'Tagging commit as {args.version}')
    subprocess.call(['git', 'tag', args.version])

    logging.info('Configuring twine for CodeArtifact and obtaining new credentials')
    subprocess.call(['aws', 'codeartifact', 'login', '--tool', 'twine',
                     '--repository', config[repository],
                     '--domain', config[domain],
                     '--domain-owner', str(config[domain_owner])])

    if package_dirs:
        for package_dir in package_dirs:
            logging.info(f'Running the tox release command for {package_dir} to build {args.version}')
            chdir(root_dir / package_dir)
            logging.debug(f'cwd: {getcwd()}')
            run_release_command()
            upload_to_codeartifact(args.version)
            chdir(root_dir)
            logging.debug(f'cwd: {getcwd()}')
    else:
        logging.info(f'Running the tox release command to build {args.version}')
        run_release_command()
        upload_to_codeartifact(args.version)

    logging.info('The release has been successfully completed - Be sure to push commits and tags to origin')

import argparse
import logging
import re
import subprocess
import sys
from os import chdir, getcwd
from pathlib import Path

from codeartifact_release import utils

version_pattern = re.compile(r'^[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}$')
package_version_file = 'PACKAGE_VERSION'
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


def version_type(arg_value: str):
    if not version_pattern.match(arg_value):
        raise argparse.ArgumentTypeError(f'Invalid version: {arg_value}, needs to be ##.##.##')
    return arg_value


def version_compare(old_version: str, new_version: str) -> bool:
    v_old = list(map(int, old_version.split('.')))
    v_new = list(map(int, new_version.split('.')))
    for old, new in zip(v_old, v_new):
        if new > old:
            return True
        elif new < old:
            return False
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


def update_package_version_file(root_dir: Path, version: str):
    logging.info(f'Updating {package_version_file}')
    with open(str((root_dir / package_version_file)), 'w') as f:
        f.write(f'{version}\n')


def main():
    config = utils.get_config()

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
            run_release_command()
            chdir(root_dir)
    else:
        logging.info('Running the tox release command')
        run_release_command()

    update_package_version_file(root_dir, args.version)
    logging.info(f'Committing {package_version_file} update')
    subprocess.call(['git', 'add', package_version_file])
    subprocess.call(['git', 'commit', '-m', f'Release {args.version}'])

    logging.info(f'Tagging commit as {args.version}')
    subprocess.call(['git', 'tag', args.version])

    logging.info('Configuring twine for CodeArtifact and obtaining new credentials')
    subprocess.call(['aws', 'codeartifact', 'login', '--tool', 'twine',
                     '--repository', config[utils.REPOSITORY],
                     '--domain', config[utils.DOMAIN],
                     '--domain-owner', str(config[utils.DOMAIN_OWNER])])

    if package_dirs:
        for package_dir in package_dirs:
            logging.info(f'Running the tox release command for {package_dir} to build {args.version}')
            chdir(root_dir / package_dir)
            run_release_command()
            upload_to_codeartifact(args.version)
            chdir(root_dir)
    else:
        logging.info(f'Running the tox release command to build {args.version}')
        run_release_command()
        upload_to_codeartifact(args.version)

    logging.info('The release has been successfully completed - Be sure to push commits and tags to origin')

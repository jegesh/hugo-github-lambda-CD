import json
import logging
import os
import shutil
import subprocess

logger = logging.getLogger('hugo-builder')
logging.getLogger().setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO")))


def load_branch_map_config(repo_dir):
    if os.path.exists(os.path.join(repo_dir, 'branch_map.json')):
        with open(os.path.join(repo_dir, 'branch_map.json')) as src:
            branch_map = json.load(src)
        return branch_map
    return None


def get_config_param(branch_name, param_name, branch_map):
    env_val = os.getenv(param_name, '')
    if branch_map and branch_name in branch_map and param_name in branch_map[branch_name]:
        return branch_map[branch_name][param_name]
    return env_val


def handler(event, context):
    headers = event['headers']
    if 'x-github-event' not in headers or headers['x-github-event'] != 'push':
        return {"statusCode": 401}
    body = json.loads(event['body'])
    repo_name = body['repository']['full_name']
    branch_name = body['ref'].split('/')[-1]
    repo_dir = repo_name.split('/')[-1]

    branch_map = load_branch_map_config(repo_dir)
    logger.debug(f'branch map= {branch_map}')

    # branch name validation
    if 'BRANCH_NAME' in os.environ and not branch_map:
        if branch_name != os.environ['BRANCH_NAME']:
            logger.info(f'Branch {branch_name} not configured for building - aborting.')
            return
    elif branch_map:
        if branch_name not in branch_map:
            logger.info(f'Branch {branch_name} not configured for building - aborting.')
            return
    else:
        raise ValueError('env var BRANCH_NAME not set and no branch map available')

    access_token = os.environ['GITHUB_ACCESS_TOKEN']
    git_username = os.environ['GITHUB_USERNAME']
    logger.info("Start clone of git repo")
    subprocess.run(
        f'git clone --depth=1 --shallow-submodules --branch {branch_name} https://{git_username}:{access_token}@github.com/{repo_name}.git',
        shell=True).check_returncode()

    logger.info('Start Hugo build process')
    base_url = get_config_param(branch_name, 'HUGO_BASE_URL', branch_map)
    hugo_flags = get_config_param(branch_name, 'HUGO_CMD_FLAGS', branch_map)
    subprocess.run(f'cd {repo_dir} && hugo -b {base_url} {hugo_flags}', shell=True).check_returncode()

    logger.info("Uploading generated web files to s3 bucket")
    bucket_name = os.environ['S3_BUCKET']
    subprocess.run(f'aws s3 cp --recursive --quiet {repo_dir}/public/ s3://{bucket_name}/')

    # remove files to prevent storage buildup
    shutil.rmtree(repo_dir)

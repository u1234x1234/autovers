#!/usr/bin/env python3
import glob
import logging
import os
import tempfile
import subprocess

import appdirs
import git

APPLICATION_NAME = 'autovers'
EXTENSIONS = ['.py']


def commit():
    """Commit all files in current directory and return string with commit hash
    """
    logger = logging.getLogger(__name__)

    working_dir = os.getcwd()
    user_data_dir = appdirs.user_data_dir(APPLICATION_NAME)

    workspace_dir = os.path.join(user_data_dir, working_dir.strip('/'))
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        logger.info('Workspace {} created.'.format(workspace_dir))

    os.environ['GIT_DIR'] = workspace_dir
    os.environ['GIT_WORK_TREE'] = os.getcwd()

    git.Repo.init(bare=False)
    repo = git.Repo()

    files = []
    for extension in EXTENSIONS:
        files += glob.glob('**/*{}'.format(extension), recursive=True)
    files = [os.path.join(working_dir, f) for f in files]

    repo.index.add(files)

    with tempfile.NamedTemporaryFile(dir='./') as tmp_file:
        out = subprocess.check_output(['pip', 'freeze', '--all'])
        tmp_file.write(out)
        tmp_file.flush()
        print(tmp_file.name)
        repo.index.add(tmp_file.name)

    if repo.head.is_valid():
        message = str(repo.head.commit.count() + 1)
    else:
        message = '1'

    repo.index.commit(message)
    return str(repo.head.commit)

commit()

#!/usr/bin/env python3
import glob
import logging
import os
import subprocess
from contextlib import contextmanager

import appdirs
import git

APPLICATION_NAME = 'autovers'
PIP_LIST_PATH = 'pip_list.txt'
CONDA_LIST_PATH = 'conda_list.txt'
AUTOVERS_EXTENSIONS_KEY = 'AUTOVERS_EXTENSIONS'
DEFAULT_EXTENSIONS = ['.py']


@contextmanager
def TemporaryFile(filename, mode='w+'):
    file = open(filename, mode=mode)
    try:
        yield file
    finally:
        file.close()
        os.remove(filename)


def commit(message='', save_pip_state=True, save_conda_state=True):
    """Commit all files in current directory and return string with commit hash
    """
    logger = logging.getLogger(__name__)

    if AUTOVERS_EXTENSIONS_KEY in os.environ:
        extensions = os.environ[AUTOVERS_EXTENSIONS_KEY].replace('.', '').split(',')
        logger.info('List of extensions from env: {}'.format(extensions))
    else:
        extensions = DEFAULT_EXTENSIONS

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
    for extension in extensions:
        files += glob.glob('**/*{}'.format(extension), recursive=True)
    files = [os.path.join(working_dir, f) for f in files]

    repo.index.add(files)

    if save_pip_state:
        with TemporaryFile(PIP_LIST_PATH) as tmp_file:
            try:
                out = subprocess.check_output(['pip', 'freeze', '--all'])
                tmp_file.write(out.decode())
                tmp_file.flush()
                repo.index.add([os.path.join(working_dir, PIP_LIST_PATH)])
            except Exception as e:
                logger.warning('Error in executing pip freeze command: {}'.format(e))

    if save_conda_state:
        with TemporaryFile(CONDA_LIST_PATH) as tmp_file:
            try:
                out = subprocess.check_output(['conda', 'list', '--export'])
                tmp_file.write(out.decode())
                tmp_file.flush()
                repo.index.add([os.path.join(working_dir, CONDA_LIST_PATH)])
            except Exception as e:
                logger.warning('Error in executing conda list command: {}'.format(e))

    repo.index.commit(message)
    return str(repo.head.commit)

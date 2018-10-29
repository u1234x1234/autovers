#!/usr/bin/env python3 
import glob
import logging
import os

import appdirs
import git

APP_NAME = 'autovers'


def commit():
    """Commit all files in current directory and return string with commit hash
    """
    CONFIG_DIR = appdirs.user_data_dir(APP_NAME)
    os.environ['GIT_DIR'] = CONFIG_DIR
    os.environ['GIT_WORK_TREE'] = os.getcwd()

    git.Repo.init(bare=False)
    repo = git.Repo()

    root_dir = os.getcwd()
    files = glob.glob('**/*.py', recursive=True)
    files = [os.path.join(root_dir, f) for f in files]

    repo.index.add(files)
    repo.index.commit('v1')

    return str(repo.head.commit)

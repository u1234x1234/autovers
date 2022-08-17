#!/usr/bin/env python3
import glob
import logging
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from subprocess import check_call
from tempfile import gettempdir
from typing import Optional

import appdirs
import git
from filelock import FileLock

PIP_LIST_PATH = "pip_list.txt"
CONDA_LIST_PATH = "conda_list.txt"
FULL_COMMAND = "command.txt"
APPLICATION_NAME = "autovers"
AUTOVERS_EXTENSIONS_KEY = "AUTOVERS_EXTENSIONS"
DEFAULT_EXTENSIONS = [".py"]
LOGGER = logging.getLogger(__name__)
LOCKFILE_PATH = f"{gettempdir()}/autovers.lock"


@contextmanager
def TemporaryFile(filename, mode="w+"):
    file = open(filename, mode=mode)
    try:
        yield file
    finally:
        file.close()
        os.remove(filename)


class IllegalArgumentError(ValueError):
    pass


@contextmanager
def patch_env_vars(dict_env: Optional[dict] = None, **kwargs_env):
    if dict_env is None:
        dict_env = {}

    if not isinstance(dict_env, dict):
        raise IllegalArgumentError("env must be dictionary")

    dict_env.update(kwargs_env)
    to_delete = [k for k, v in dict_env.items() if v is None]
    dict_env = {k: v for k, v in dict_env.items() if v is not None}

    # Save original
    original_environ = dict(os.environ)

    try:
        os.environ.update(dict_env)
        [os.environ.pop(k) for k in to_delete]
        yield
    except TypeError as e:
        raise IllegalArgumentError(e)
    finally:
        # Return original
        os.environ.clear()
        os.environ.update(original_environ)


@contextmanager
def _provide_git_repo(working_dir):
    user_data_dir = appdirs.user_data_dir(APPLICATION_NAME)

    workspace_dir = os.path.join(user_data_dir, working_dir.strip("/"), "git")

    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        LOGGER.info("Workspace {} created.".format(workspace_dir))

    with patch_env_vars(GIT_DIR=workspace_dir, GIT_WORK_TREE=os.getcwd()):
        git.Repo.init(bare=False)
        repo = git.Repo()
        yield repo


def _save_pip_state(repo, working_dir, condition):
    if condition:
        with TemporaryFile(PIP_LIST_PATH) as tmp_file:
            try:
                out = subprocess.check_output(["pip", "freeze", "--all"])
                tmp_file.write(out.decode())
                tmp_file.flush()
                repo.index.add([os.path.join(working_dir, PIP_LIST_PATH)])
            except Exception as e:
                LOGGER.warning("Error in executing pip freeze command: {}".format(e))


def _save_conda_state(repo, working_dir, condition):
    if condition:
        with TemporaryFile(CONDA_LIST_PATH) as tmp_file:
            try:
                out = subprocess.check_output(["conda", "list", "--export"])
                tmp_file.write(out.decode())
                tmp_file.flush()
                repo.index.add([os.path.join(working_dir, CONDA_LIST_PATH)])
            except Exception as e:
                LOGGER.warning("Error in executing conda list command: {}".format(e))


def _save_command(repo, working_dir, condition):
    if condition:
        with TemporaryFile(FULL_COMMAND) as tmp_file:
            print(" ".join(sys.argv), file=tmp_file)
            tmp_file.flush()
            repo.index.add([os.path.join(working_dir, FULL_COMMAND)])


def commit(
    message="",
    save_pip_state=False,
    save_conda_state=False,
    save_command=True,
    verbose=0,
):
    """Commit all files in current directory and return string with commit hash"""

    with FileLock(LOCKFILE_PATH):

        if AUTOVERS_EXTENSIONS_KEY in os.environ:
            extensions = os.environ[AUTOVERS_EXTENSIONS_KEY].replace(".", "").split(",")
            LOGGER.info("List of extensions from env: {}".format(extensions))
        else:
            extensions = DEFAULT_EXTENSIONS

        working_dir = os.getcwd()
        with _provide_git_repo(working_dir) as repo:
            files = []
            for extension in extensions:
                files += glob.glob("**/*{}".format(extension), recursive=True)
            files = [os.path.join(working_dir, f) for f in files]

            repo.index.add(files)

            _save_pip_state(repo, working_dir, save_pip_state)
            _save_conda_state(repo, working_dir, save_conda_state)
            _save_command(repo, working_dir, save_command)

            r_commit = repo.index.commit(message)
            if verbose:
                print("[Autovers] Number of commits: ", working_dir, r_commit.count())

        # Clone
        path = appdirs.user_data_dir(APPLICATION_NAME)
        path = os.path.join(path, working_dir.strip("/"))
        shutil.rmtree(path + "/source_code", ignore_errors=True)
        command = ["git", "clone", path + "/git", path + "/source_code"]
        check_call(command, stderr=subprocess.DEVNULL)

    return r_commit.hexsha


def last_diff():
    formatted_diffs = []

    working_dir = os.getcwd()
    with _provide_git_repo(working_dir) as repo:
        # create_patch is slower but returns the full diff information
        diffs = repo.commit("HEAD~1").diff(repo.head, create_patch=True)
        for d in diffs:
            formatted_diffs.append((d.a_path, d.diff.decode()))

    return formatted_diffs

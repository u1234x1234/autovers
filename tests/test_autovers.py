import os
import tempfile
from unittest import mock

import git

import autovers


def test_commit():
    # Create tmp directory for GIT workspace
    with tempfile.TemporaryDirectory() as tmp_dir:

        # Do not use default ~/.local/ directory, save to temporary
        with mock.patch('appdirs.user_data_dir') as patched_func:
            patched_func.return_value = tmp_dir

            experiment_name = autovers.commit()

            work_dir = os.path.join(tmp_dir, os.getcwd().strip('/'))
            os.environ['GIT_DIR'] = work_dir

            repo = git.Repo()
            assert repo.head.commit.count() == 1
            assert repo.head.commit.message == ''

            # check commit message
            message = 'commit_message'
            experiment_name = autovers.commit(message)
            assert repo.head.commit.message == message


def test_temp_file():
    filename = 'temp_file'

    with autovers.TemporaryFile(filename) as out_file:
        print('TMP FILE', file=out_file)
        assert os.path.exists(filename) is True

    assert os.path.exists(filename) is False

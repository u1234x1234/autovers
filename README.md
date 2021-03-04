[![Build Status](https://travis-ci.org/u1234x1234/autovers.svg?branch=master)](https://travis-ci.org/u1234x1234/autovers)
[![Coverage Status](https://coveralls.io/repos/github/u1234x1234/autovers/badge.svg?branch=master)](https://coveralls.io/github/u1234x1234/autovers?branch=master)

# autovers

A simple tool for experiment tracking.

## Usage:
```python
import autovers

experiment_hash = autovers.commit()
```

Show autovers-related git repo:
```bash
autovers git status
autovers gitk
```

Suppose you current dir is `/home/path/to/your/project/`.

It will create a completely new git repo (if not existed) that does not related to the one from `/home/path/to/your/project/`

New git repo will be located:

- /home/user_name/.local/share/autovers/home/path/to/your/project/
    - git/          - directory contains .git content
    - source_code/   - sources, will be the same as `/home/path/to/your/project/` except the ignored files

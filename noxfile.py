import os
from pathlib import Path
import subprocess as sp

_PYENV_ROOT = Path(sp.run(['pyenv', 'root'], encoding='utf8', stdout=sp.PIPE).stdout.strip())
_PYENV_PATH_EXTENSION = ''.join(f":{p}" for p in _PYENV_ROOT.glob('versions/*/bin'))

# As much as we hate virtualenvs, we use them here for simplicity in
# multi-version testing (and so we don't taint our `python_packages`)
os.environ.update({
    'PATH': f"{os.environ['PATH']}{_PYENV_PATH_EXTENSION}",
    'POETRY_VIRTUALENVS_CREATE': 'false',
})

import nox


@nox.session(python=['3.10', '3.11'])
def test(session):
    session.run('poetry', 'install', external=True)
    session.run('pytest')

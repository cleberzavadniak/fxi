#!/bin/zsh

set -e

# export PYENV_VERSION=pypy3.5-5.10.1
export PYTHONPATH=fxi
export FXIPATH="$PWD/applications:$HOME/fxi-apps"

python3 -m fxi $*

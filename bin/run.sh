#!/bin/zsh

set -e

time for file in **/*.coco;do
    coconut --target 36 $file
done

# export PYENV_VERSION=pypy3.5-5.10.1
export PYTHONPATH=fxi
export FXIPATH="$PWD/applications:$HOME/fxi-apps"

python3 -m fxi $*

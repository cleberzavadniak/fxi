#!/bin/zsh

set -e

for file in **/*.coco;do
    coconut --target 36 $file
done

# export PYENV_VERSION=pypy3.5-5.10.1
export PYTHONPATH=fxi

python3 -m fxi $*

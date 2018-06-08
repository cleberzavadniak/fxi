#!/bin/zsh

set -e

for file in **/*.coco;do
    coconut --target 36 $file
done

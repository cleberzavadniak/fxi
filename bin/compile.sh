#!/bin/zsh

set -e

if [[ $FXIPATH == "" ]];then
    export FXIPATH="$PWD/applications:$HOME/fxi-apps"
fi

path_str=$(echo $FXIPATH | sed "s/:/ /g")
eval "dirs=($path_str)"

print "dirs: $dirs"

for d in $dirs;do
    [[ -d $d ]] || continue
    (
        echo $d
        cd $d
        for file in **/*.coco;do
            coconut --target 36 $file
        done
    )
done

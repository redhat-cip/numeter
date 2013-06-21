#!/bin/bash

export DIST=${1:-"wheezy"}
export ARCH=${2:-"amd64"}

echo Build package : $DIST - $ARCH

dpkg -l git-buildpackage > /dev/null 2>&1
if [ $? -eq 1 ];then
    echo ERROR git-buildpackage not found
fi

if [ -d "/var/cache/pbuilder/base-$DIST-$ARCH.cow" ];then
    git-pbuilder update
else
    git-pbuilder create
fi

BUILD_DIR=$(mktemp -d)

cd $BUILD_DIR
gbp-clone --debian-branch=debian-$DIST --upstream-branch=stable https://github.com/enovance/numeter
cd numeter
#git-buildpackage --git-prebuild="git merge stable -m merge" --git-pbuilder --git-verbose
git-buildpackage --git-debian-branch=debian-$DIST --git-upstream-branch=stable --git-arch=$ARCH --git-dist=$DIST --git-prebuild="git merge stable -m merge" --git-pbuilder --git-verbose
rm -rf $BUILD_DIR

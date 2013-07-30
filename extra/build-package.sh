#!/bin/bash

export DIST=${1:-"wheezy"}
export ARCH=${2:-"amd64"}

REPO="numeter"
GIT_URL="https://github.com/enovance/$REPO"
UPSTREAM_BRANCH=${UPSTREAM_BRANCH:-"stable"}
BUILD_DIR=$(mktemp -d)
export GIT_PBUILDER_OUTPUT_DIR="$BUILD_DIR/build-result"

mkdir -p $GIT_PBUILDER_OUTPUT_DIR

echo Build package : $DIST - $ARCH from $UPSTREAM_BRANCH

dpkg -l git-buildpackage > /dev/null 2>&1
if [ $? -eq 1 ];then
    echo ERROR git-buildpackage not found
fi

dpkg -l quilt > /dev/null 2>&1
if [ $? -eq 1 ];then
    echo ERROR quilt not found
fi

if [ -d "/var/cache/pbuilder/base-$DIST-$ARCH.cow" ];then
    git-pbuilder update
else
    git-pbuilder create
fi

cd $BUILD_DIR
gbp-clone --debian-branch=debian-$DIST --upstream-branch=$UPSTREAM_BRANCH $GIT_URL

cd $REPO

git-buildpackage \
--git-debian-branch=debian-$DIST \
--git-upstream-branch=$UPSTREAM_BRANCH \
--git-arch=$ARCH \
--git-dist=$DIST \
--git-prebuild="git merge $UPSTREAM_BRANCH -m merge ; sed -i \"1s/(\(.*\))/(\\1-0+${DIST})/\" debian/changelog" \
--git-pbuilder \
--git-verbose

echo "Build results : $GIT_PBUILDER_OUTPUT_DIR"

ls -latrh $GIT_PBUILDER_OUTPUT_DIR

rm -rf $BUILD_DIR

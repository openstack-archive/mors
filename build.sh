#!/bin/sh
set -e
source ../pf9-version/pf9-version.rc
export ROOT_DIR=`pwd`
cd $ROOT_DIR/support/
make all

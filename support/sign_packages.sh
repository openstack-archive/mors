#!/bin/sh

if [ "x${SIGN_PACKAGES}" = "x1" ]; then
    expect $(dirname $0)/mors.expect $@
fi

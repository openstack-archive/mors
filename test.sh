#!/usr/bin/env bash
# Copyright (c) Platform9 systems. All rights reserved
output_dir=./build
log_filter=-paramiko.transport
setup_venv() {
    virtualenv ${output_dir}/venv
    source ${output_dir}/venv/bin/activate
    pip install -e .
}

run_tests() {
    python ./test/run_tests.py --verbose --with-xunit --xunit-file=${output_dir}/test_output.xml \
              --logging-clear-handlers ${exclude} ${nocapture} --logging-filter=${log_filter} ${module} \
              --logging-format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
}

setup_venv
run_tests


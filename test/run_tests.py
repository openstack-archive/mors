# Copyright (c) 2016 Platform9 Systems Inc.
# All Rights reserved

def run_tests():
    from proboscis import TestProgram
    import test_api

    # Run Proboscis and exit.
    print "Starting tests ---"
    TestProgram().run_and_exit()
    print "Tests done ---"

if __name__ == '__main__':
    print "Run tests"
    run_tests()
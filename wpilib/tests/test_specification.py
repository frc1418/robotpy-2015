
import importlib.machinery
import io
import os
from os.path import abspath, dirname, exists, join
import shutil
import zipfile

import pytest

hal_dir = abspath(join(dirname(__file__), '__hal__'))
hal_version_file = join(hal_dir, 'version')

hal_setup_py = abspath(join(dirname(__file__), '..', '..', 'hal-roborio', 'setup.py'))

def _download_hal_includes():
    
    hal_setup = importlib.machinery.SourceFileLoader('hal_setup_py',
                                                     hal_setup_py).load_module()
    
    print("Using HAL", hal_setup.hal_version)
    print()
    
    if exists(hal_dir):
        # find the version
        if exists(hal_version_file):
            with open(hal_version_file) as fp:
                hal_version = fp.read().strip()
                
            if hal_version == hal_setup.hal_version:
                return
            
        # Nope, gotta download a new distribution
        shutil.rmtree(hal_dir)
    
    # Download the hal zipfile
    hal_download_zip = hal_setup.hal_download_zip
    if hal_download_zip is None:
        hal_download_zip = hal_setup.download_halzip()
    
    os.mkdir(hal_dir)
    
    with zipfile.ZipFile(hal_download_zip) as z:
        z.extractall(hal_dir)
        
    # write the version to a file
    with open(hal_version_file, 'w') as fp:
        fp.write(hal_setup.hal_version + '\n')


def test_check_hal_api(hal):
    '''
        This test checks the HAL API against the include files that our Jenkins
        buildbot zips up when it builds our HAL shared library. If they don't
        match, then it may result in memory corruption or segfaults.
        
        This test ensures that the HAL shared library can be downloaded, and 
        also checks our HAL against the one that we claim to be compiled against.
    '''
    
    _download_hal_includes()
    
    from spec_scanners import hal_scanner

    hal_dirs = hal_scanner.get_hal_dirs(hal_dir)
    for tree in hal_dirs:
        assert exists(tree), "Invalid HAL include directory"

    frontend_output = hal_scanner.compare_header_dirs([hal], hal_dirs)
    backend_output = hal_scanner.scan_c_end(hal, frontend_output)
    
    has_errors = False
    
    for item in backend_output["methods"]:
        if len(item["errors"]) > 0:
            has_errors = True
            print("Error: method call to {} doesn't match c++ spec.".format(item["name"]))
            for error in item['errors']:
                print("- ", error)
            print()
            
    for item in backend_output["classes"]:
        if item["errors"] > 0:
            has_errors = True
            print("Error: class {} doesn't match c++ spec, and is not ignored.".format(item["name"]))
            for error in item['errors']:
                print("- ", error)
            print()

    assert has_errors == False, "Check stdout for failure details"


@pytest.mark.skipif(os.getenv('WPILIB_JAVA_DIR', None) == None,
                    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test")
def test_check_wpilib_api(wpilib):
    '''
        These just check to see if our implementation is in line with
        the WPILib implementation. Not critical.
    '''

    from spec_scanners import wpilib_scanner

    wpilibj_dirs = wpilib_scanner.get_wpilib_dirs(os.environ['WPILIB_JAVA_DIR'])
    for tree in wpilibj_dirs:
        assert exists(tree), "WPILIB_JAVA_DIR does not point to wpilib tree dir"

    output = wpilib_scanner.compare_folders(wpilib, wpilibj_dirs)

    for item in output["children"]:
        if item["errors"] > 0:
            assert False, "Error: item {} doesn't match java spec, and is not ignored.".format(item["name"])

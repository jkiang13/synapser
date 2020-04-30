import sys   
import pip
import os
import urllib
import gzip
import tarfile
import shutil
import distutils.core
import distutils.log
import platform
from setuptools.command.install import install
import tempfile
import time
import importlib
import pkg_resources
import glob
import zipfile
import subprocess
from patchStdoutStdErr import patch_stdout_stderr
import time

# in a stable way across python versions. the typical approach is to
# call pip in a subprocess using sys.executable, but running inside
# PythonEmbedInR sys.executable may not be what we want.
try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

def localSitePackageFolder(root):
    if os.name=='nt':
        # Windows
        return root+os.sep+"Lib"+os.sep+"site-packages"
    else:
        # Mac, Linux
        return root+os.sep+"lib"+os.sep+"python3.6"+os.sep+"site-packages"
    
def addLocalSitePackageToPythonPath(root):
    # clean up sys.path to ensure that synapser does not use user's installed packages
    sys.path = [x for x in sys.path if x.startswith(root) or "PythonEmbedInR" in x]

    sitePackages = localSitePackageFolder(root)
    # PYTHONPATH sets the search path for importing python modules
    if os.environ.get('PYTHONPATH') is not None:
      os.environ['PYTHONPATH'] += os.pathsep+sitePackages
    else:
      os.environ['PYTHONPATH'] = os.pathsep+sitePackages
    sys.path.append(sitePackages)
    # modules with .egg extensions (such as future and synapseClient) need to be explicitly added to the sys.path
    for eggpath in glob.glob(sitePackages+os.sep+'*.egg'):
        os.environ['PYTHONPATH'] += os.pathsep+eggpath
        sys.path.append(eggpath)

def main(path):
    patch_stdout_stderr()

    path = pkg_resources.normalize_path(path)
    moduleInstallationPrefix=path+os.sep+"inst"

    localSitePackages=localSitePackageFolder(moduleInstallationPrefix)

    addLocalSitePackageToPythonPath(moduleInstallationPrefix)

    os.makedirs(localSitePackages)
    install_target = "Installing to {}".format(localSitePackages)
    target_exists = "Exists? {}".format(os.path.exists(localSitePackages))
    target_is_dir = "is dir {}".format(os.path.isdir(localSitePackages))
    executable = "executable {}".format(sys.executable)
    print(install_target)
    print(target_exists)
    print(target_is_dir)


    
    # The preferred approach to install a package is to use pip...
#    call_pip('pandas==0.22', localSitePackages)
#    call_pip('certifi', localSitePackages) 
#    call_pip('synapseclient==2.0.0', localSitePackages)
#    call_pip('MarkupSafe==1.0', localSitePackages)
#    call_pip('Jinja2==2.8.1', localSitePackages)

    out_path = "/tmp/debug.out"
    if 'win' in platform.platform().lower():
        out_path = "c:/debug.out"

    with open(out_path, 'a') as out_file:
       out_file.write(executable)
       out_file.write(install_target)
       out_file.write('\n' + localSitePackages)
       time.sleep(100)

       for package in (
           'pandas==0.22',
           'certifi',
           'synapseclient==2.0.0',
           'MarkupSafe==1.0',
           'Jinja2==2.8.1'
       ):
           rc = subprocess.call([sys.executable, "-m", "pip", "install", package, "--upgrade", "--quiet", "--target", localSitePackages], stdout=out_file, stderr=out_file)
           if rc != 0:
               raise Exception("pip.main returned {} when installing {}".format(rc, package))

    addLocalSitePackageToPythonPath(moduleInstallationPrefix) 


# pip installs in the wrong place (ends up being in the PythonEmbedInR package rather than this one)
def call_pip(packageName, target):
        rc = pipmain(['install', packageName, '--upgrade', '--quiet', '--target', target])
        if rc!=0:
            raise Exception('pip.main returned '+str(rc))


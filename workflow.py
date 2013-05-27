# DMG Install Workflow for Alfred v2
#
# -----------------------------------------------------------------------------
# "THE NERD-WARE LICENSE" (Revision 1): <dev.git@lc3dyr.de> wrote this file.
# As long as you retain this notice you can do whatever you want with this
# stuff. If we meet some day, and you think this stuff is worth it, you can buy
# me a beer, mate or some food in return [Franz Greiling]
# -----------------------------------------------------------------------------
#   
# by laerador (Franz Greiling)

import alp
from send2trash import send2trash

import sys
import os.path
import time

import errno
import subprocess

import zipfile
from tempfile import mkdtemp

import shutil


'''
Basic Functions for Finding, Mounting and Installing
'''
def find_dmg(directory='~/Downloads/'):
    """ Searches 'directory' for all files ending with *.dmg """
    directory = os.path.expanduser(directory)

    # Find all DMGs
    dmgs = []
    for f in os.listdir(directory):
        if f.endswith('.dmg'):
            dmgs.append(os.path.join(directory, f))

    return dmgs

def find_zip(directory='~/Downloads/'):
    """ Searches 'directory' for all zip-Files containing *.apps """
    directory = os.path.expanduser(directory)
    
    # Find all zips
    zips = []
    for f in os.listdir(directory):
        if f.endswith('.zip'):
            zf = zipfile.ZipFile(os.path.join(directory, f), 'r')
            if [x.split('.app/', 1)[0]+'.app/' for x in zf.namelist() if x.count('.app/') == 1]:
                zips.append(os.path.join(directory, f))

    return zips


def find_install_app(directory, installto='/Applications/'):
    """ Finds an App in 'path' and installs it """
    
    # Find all DMGs
    apps = []
    for f in os.listdir(directory):
        if f.endswith('.app'):
            apps.append(os.path.join(directory, f))

    # Copy all apps to Install-Directory
    for app in apps:
        return_code = subprocess.call(['cp', '-pR', app, installto])
        if return_code != 0:
            print(errno.errorcode[return_code])
            print(return_code)
            sys.exit(1)

    return len(apps)


def mount_dmg(dmg,unmount=False):
    """ (Un)Mounts given DMG at /Volumes/NAME """
    
    # Generate Mountpoint
    mount_point = os.path.join('/Volumes/', os.path.splitext(os.path.basename(dmg))[0])

    # Mount dmg
    dnull = open('/dev/null','w')
    if unmount:
        return_code = subprocess.call(['hdiutil', 'detach', volume], stdout=dnull)
    else:
        return_code = subprocess.call(['hdiutil', 'attach', '-mountpoint', mount_point, dmg], stdout=dnull)
    if return_code is not 0:
        print(errno.errorcode[return_code])
        sys.exit(1)

    return mount_point

def extract_from_zip(zipf):
    """ Extracts all Apps from zipfile to temp-directory, 
    then calls find_install_app() """
    
    zf = zipfile.ZipFile(zipf,'r')
    d = mkdtemp()
    for app in list(set([x.split('.app/',1)[0]+'.app/' for x in zf.namelist() if x.count('.app/') == 1])):
        return_code = subprocess.call(['unzip', '%s'%zipf, '%s'%app, '-d', '%s'%d])
        if return_code != 0:
            print(errno.errorcode[return_code])
            print(return_code)
            sys.exit(1)

    return find_install_app(d)


'''
Functions for the use with Alfred
'''
def file_action(f,delete=False):
    if f.endswith('.dmg'):
        vol = mount_dmg(f)
        nr = find_install_app(vol)
        mount_dmg(f,unmount=True)
    elif f.endswith('.zip'):
        nr = extract_from_zip(f)

    if nr is 0:
        print('No Apps where installed')
        return
    elif nr is 1:
        print('1 App was installed')
    elif nr > 0:
        print('%d Apps where installed'%nr)

    if delete:
        try:
            send2trash(f)
        except OSError:
            pass

def script_action():
    """Creates Alfred-Feedback for the most-recent DMG"""
    matches = find_dmg()
    matches+= find_zip()

    # Sort by Creation time; Newest come first
    matches = sorted(matches, key=lambda f: os.path.getctime(f), reverse=True)

    fb = []
    if matches:
        for match in matches:
            fb.append(alp.Item(**{
                'title': 'Install %s'%(os.path.splitext(os.path.basename(match))[0],),
                'subtitle': 'Install all Apps from %s'%match,
                'arg': match,
                'fileIcon': match,
                'fileType': 'True'}))
    else:
        fb.append(alp.Item(**{
            'title': 'Install dmg',
            'subtitle': 'No dmg found',
            'valid': no}))

    alp.feedback(fb)

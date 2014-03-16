#!/usr/bin/env python
"""
Provides a Class to find and install Mac OS X Applications

The install module provides an easy interface to find installable objects on
Mac OS X. An installable object is any of the following:
    1. an Application Bundle ('.app')
    2. a OS X Install-Package ('.pkg')
    3. an Alfred Workflow ('.alfredworkflow')
    4. a Disk Image containing any of the above ('.dmg')
    5. a Zipfile containing any of 1-3 ('.zip')
"""

import os.path
import logging
import logging.handlers
import zipfile
import errno
import subprocess
import tempfile

import send2trash

__author__ = "Franz Greiling"
__email__ = "dev.installpy@lc3dyr.de"
__copyright__ = "Copyright (c) 2014, Franz Greiling"
__licence__ = "BSD 2-Clause License"
__version__ = "v1.0"


# Setting up Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter_ch = logging.Formatter(
    '%(asctime)s - %(name)s <%(levelname)s>\n%(message)s\n'
)
formatter_sl = logging.Formatter(
    '%(name)s: %(levelname)s %(message)s'
)

syslog = logging.handlers.SysLogHandler(address="/var/run/syslog")
syslog.setLevel(logging.WARNING)
syslog.setFormatter(formatter_sl)
logger.addHandler(syslog)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter_ch)
logger.addHandler(console)


def mount_dmg(dmg, unmount=False):
    """ (Un)Mounts given DMG at /Volumes/NAME """

    # Generate Mountpoint
    mount_point = os.path.join('/Volumes/',
                               os.path.splitext(os.path.basename(dmg))[0])

    # Mount dmg
    dnull = open('/dev/null', 'w')
    if unmount:
        logger.info("Unmounted %s")
        return_code = subprocess.call([
            'hdiutil',
            'detach',
            mount_point
        ], stdout=dnull)
    else:
        logger.info("Mounted %s at %s" % (dmg, mount_point))
        return_code = subprocess.call([
            'hdiutil',
            'attach',
            '-mountpoint',
            mount_point,
            dmg
        ], stdout=dnull)

    # Minimal Error Handling
    if return_code != 0:
        logger.error("%d: %s" %
                     (return_code, errno.errorcode[return_code]))
        raise OSError(return_code)

    return mount_point


class NoApplicationException(Exception):
    pass


class NotInstalledException(Exception):
    pass


class Installable(object):
    """
    Specifices an installable object.
    """

    #: List of Acceptable Types
    TYPES = [
        '.dmg',
        '.zip',
        '.pkg',
        '.app',
        '.alfredworkflow',
    ]

    #: List of Search Paths
    PATHS = [
        '~/Downloads/',
        # '~/Desktop/',
    ]

    def __init__(self, path, types=TYPES):
        """
        Creates new Instance of Installable from path.

        During initialization, zipfiles are inspected to find any possible
        Installable inside them.

        Args:
            path: Object to reference in this Instance
                REQUIRED
            types: Types which to accept in path. Needs to be a subset of TYPES
                Defaults to TYPES

        Raises:
            NoApplicationException: is raised when the type of 'path' is not in
                TYPES, i.e. not recognized.
                This is also true if type is '.zip', but this '.zip' does not
                contain any valid Installables.
        """
        path = path.rstrip('/')
        ext = os.path.splitext(path)[1]

        # Check if path is a valid File
        if ext not in types:
            logger.debug("%s is no valid Installable object." % path)
            raise NoApplicationException()

        # Special Zip Treatment
        # Only accept zips, if they include a valid type
        # Inside zips, ignore .zips and .dmgs
        inzip = []

        if ext == '.zip':
            _types = list(types)
            _types.remove('.zip')
            _types.remove('.dmg')

            zf = zipfile.ZipFile(path, 'r')

            for f in zf.namelist():
                if f.startswith("__MACOSX/"):
                    continue

                t = os.path.splitext(f.rstrip('/'))[1]
                if t in _types and f.count(t+'/') == 1:
                    logger.info("Found Installable %s inside %s" % (f, path))
                    inzip.append(f.split('.app/', 1)[0]+'.app/')

            if not inzip:
                logger.debug("No Installables in %s" % path)
                raise NoApplicationException()

        self.inzip = set(inzip)
        self.path = path
        self.ext = ext

    def _install_app(self, prefix, overrite=False, remove=False):
        dest = os.path.join(prefix, os.path.basename(self.path))
        if os.path.exists(dest):
            if overrite:
                logger.debug("Trying to remove %s" % (dest))
                send2trash.send2trash(dest)
                logger.info("Moved %s to trash." % dest)
            else:
                logger.error("File exists: %s" % dest)
                raise OSError(17, "File exists", dest)

        logger.debug(
            "Installing: %s" % os.path.basename(self.path))
        return_code = subprocess.call(
            ['/bin/cp', '-a', self.path, prefix])

        # Minimal Error handling
        if return_code != 0:
            logger.error("%d: %s" %
                         (return_code, errno.errorcode[return_code]))
            raise OSError(return_code)

        logger.info("Installed %s to %s" % (self, prefix))

    def _install_zip(self, prefix, overrite=False, remove=False):
        tmp = tempfile.gettempdir()

        return_code = subprocess.call(
            ['unzip', '-u', '-o', self.path, '-d', tmp]
        )

        # Minimal Error handling
        if return_code != 0:
            logger.error("%d: %s" %
                         (return_code, errno.errorcode[return_code]))
            raise OSError(return_code)

        for f in self.inzip:
            a = Installable(os.path.join(tmp, f))
            a.install(prefix, overrite=overrite)

    def _install_dmg(self, prefix, overrite=False, remove=False):
        where = mount_dmg(self.path)

        apps = self.get_installables(path=where)
        for app in apps:
            app.install(prefix, overrite=overrite)

        mount_dmg(self.path, unmount=True)

    def _install_pkg(self, prefix=None, overrite=False, remove=False):
        return_code = subprocess.call(['open', '-W', self.path])

        # Minimal Error handling
        if return_code != 0:
            logger.error("%d: %s" %
                         (return_code, errno.errorcode[return_code]))
            raise OSError(return_code)

    def _install_alfredworkflow(self, prefix="/",
                                overrite=False, remove=False):
        if remove:
            tmp = tempfile.gettempdir()

            return_code = subprocess.call(
                ['/bin/cp', '-a', self.path, tmp])

            # Minimal Error handling
            if return_code != 0:
                logger.error("%d: %s" %
                            (return_code, errno.errorcode[return_code]))
                raise OSError(return_code)

            path = os.path.join(tmp, os.path.basename(self.path))
        else:
            path = self.path

        return_code = subprocess.call(
            ['open', path]
        )

        # Minimal Error handling
        if return_code != 0:
            logger.error("%d: %s" %
                         (return_code, errno.errorcode[return_code]))
            raise OSError(return_code)

    def install(self, prefix='/Applications/', remove=False, overrite=False):
        """
        Installs the Applications referenced by this Instance.

        This method is mainly a wrapper around type-specific install functions.

        Args:
            prefix: Path to where Applications ('.app') shall be installed.
                Defaults to '/Applications/'.
                Note: This prefix will only be used for ('.app')-Files and
                ignored otherwise.
            remove: Boolean. If set to 'True', method will try to remove
                Object after successful installation.
                Defaults to 'False'
            overrite: Boolean. If set to 'True', will overrite existing Apps at
                path.
                Defaults to 'False'

        Returns:
            Original Path of the referenced object on success, None otherwise.

        Raises:
            OSError: is raised on several occasions, when installation failed.
                This can for example happen, when you dont have Permissions at
                path.
        """

        logger.debug(
            "Trying to install %s to %s with remove %s and overrite %s" %
            (self.path, prefix, remove, overrite))
        try:
            if self.removed:
                logger.warning("%s has been removed!" % self)
                return None
        except AttributeError:
            pass

        getattr(self, "_install" + self.ext.replace('.', "_"))(
            prefix=prefix,
            overrite=overrite,
            remove=remove,
        )
        logger.info("Installed %s to %s" % (self, prefix))

        self.installed = True

        if remove:
            self.remove()

        return self.path

    def remove(self, force=False):
        """
        Removes the Container of Applications (dmgs, zips, pkgs).

        This method can only be called after install() has run succesfully.

        Args:
            force: If set, Installable will be removed even if it has not been
                installed. Defaults to 'False'

        Raises:
            NotInstalledException: If Installable().install has not been called
                successfully and force is 'False'
        """

        if not self.installed and not force:
            logger.debug("Cant remove %s!" % self)
            raise NotInstalledException()

        try:
            send2trash.send2trash(self.path)
            self.removed = True
            logger.info("Moved %s to trash." % self)
        except OSError as ose:
            logger.exception(ose)

    def __len__(self):
        """returns number of installable objects"""
        return 1 if len(self.installable) == 0 else len(self.installable)

    def __repr__(self):
        """gives a representation of the instance"""
        return "<" + self.__class__.__name__ + ": " + str(self) + ">"

    def __str__(self):
        """returns __unicode__"""
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        """gives the basename of the referenced installable object"""
        return os.path.basename(self.path)

    # Static Methods
    def get_installables(paths=PATHS, types=TYPES):
        """
        Finds installable objects

        Args:
            paths: List of Path in which to look for installable objects.
                Defaults to Installable.PATHS
            types: List of Types to recognize as installable objects. Must be
                a subset of Installable.TYPES. Defaults to Installable.TYPES

        Returns:
            a List of Installable() objects.
        """

        inst = []

        for p in paths:
            p = os.path.expanduser(p)
            for f in os.listdir(p):
                try:
                    i = Installable(os.path.join(p, f), types=types)
                    logger.info("Found Installable at '%s'" % i.path)
                    inst.append(i)
                except NoApplicationException:
                    logger.log(logging.NOTSET, "No valid Installable at %s")

        return inst

#!/usr/bin/env python
"""
Functions for the use with Alfred v2 on Mac OS X
"""

import os.path
import string

import alp
from install import Installable, logger, NoApplicationException

__author__ = "Franz Greiling"
__email__ = "dev.installpy@lc3dyr.de"
__copyright__ = "Copyright (c) 2014, Franz Greiling"
__licence__ = "BSD 2-Clause License"
__version__ = "v1.0"


def list_installables(query=None,
                      paths=Installable.PATHS,
                      types=Installable.TYPES):
    """
    searches for Installables in 'path' and generates Alfred-Feedback

    Args:
        query: Filters the resuls using a substring search
        paths: List of paths that are searched for Installables
        types: List of types that are used for Installables

    Returns:
        Returns Alfred Feedback XML containing one Item per Installable
    """

    apps = Installable.get_installables(paths, types)

    # Sort by Creation time; Newest come first
    apps = sorted(apps,
                  key=lambda f: os.path.getctime(f.path),
                  reverse=True)

    fb = []
    for a in apps:
        if query and string.find(str(a).lower(), query.lower()) == -1:
            continue

        fb.append(alp.Item(**{
            'title': "Install %s" % os.path.splitext(str(a))[0],
            'subtitle': "Install this %s" % a.ext.lstrip('.'),
            'arg': a.path,
            'filetype': a.path,
        }))

    alp.feedback(fb)


def install(query, prefix='/Applications/', overrite='True', remove=False):
    """
    Installs the Object at 'query'

    Args:
        query: REQUIRED: full path to the Installable
        prefix: Defines where '.app's shall be installed.
            Default is '/Applications/'
        overrite: Defines if Applications at 'prefix' shall be overwritten
            Default is 'True'
        remove: If set to 'True' will remove the Installable after installation
            Default is 'False'

    Returns:
        Returns a string containing information about success or failure
    """

    try:
        app = Installable(query)
        ret = app.install(
            prefix=prefix,
            remove=remove,
            overrite=overrite
        )
        if ret != app.path:
            print("Error installing Application")
        else:
            number = len(app)
            if number == 1:
                print("1 App was installed")
            else:
                print("%d Apps were installed" % number)
    except NoApplicationException:
        logger.error(
            "Could not install %s: No valid application found" % query)
        print("No valid application found.")
        return
    except OSError:
        print("Error installing Application")
        return

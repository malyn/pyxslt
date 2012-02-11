#!/usr/bin/env python

# Python imports.
import re
import sys

# Distutils imports.
from distutils.core import setup

# pyxslt imports.
import pyxslt


# Set the distribution name.
NAME = 'pyxslt'

# Get the metadata from the pyxslt package.
VERSION = str(pyxslt.__version__)
(AUTHOR, EMAIL) = re.match('^(.*?)\s*<(.*)>$', pyxslt.__author__).groups()
URL = pyxslt.__url__
LICENSE = pyxslt.__license__

# Patch distutils if it can't cope with the 'classifiers' or
# 'download_url' keywords.
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Set the long description.
long_description = """
pyxslt makes it easy to turn Python objects into XML documents.  In
addition to basic XML serialization, pyxslt can also apply an XSL
stylesheet to the serialized XML fragments.  You could, for example, use
pyxslt to convert the results of an SQLObject_ query to an XHTML file.

All Python objects given to pyxslt are converted into their string
representations.  pyxslt focuses on serializing objects in such a way as
to make the construction of XSL stylesheets as easy as possible.  As a
result, pyxslt's XML serialization is usually not reversible.

In other words, pyxslt is not a replacement for pickle_, marshal_,
shelve_, or any of the other true serialization modules.  pyxslt is
designed with one-way XSL transformation in mind.

pyxslt makes use of libxml2_ to build its internal XML documents and
libxslt_ to perform XSL transformations.  Both packages must be
installed in order for pyxslt to do its job.

.. _SQLObject: http://sqlobject.org/
.. _pickle: http://docs.python.org/lib/module-pickle.html
.. _marshal: http://docs.python.org/lib/module-marshal.html
.. _shelve: http://docs.python.org/lib/module-shelve.html
.. _libxml2: http://xmlsoft.org/
.. _libxslt: http://xmlsoft.org/XSLT/
"""

# Configure distutils.
setup(name=NAME,
      version=VERSION,
      description='Serialize Python objects to XML using an XSL stylesheet.',
      long_description=long_description,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
      ],
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=URL,
      download_url='%s%s-%s.tar.gz' % (URL, NAME, VERSION),
      scripts=['scripts/pyxslt'],
      packages=['pyxslt'])

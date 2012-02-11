# Copyright (c) 2006, Michael Alyn Miller <malyn@strangeGizmo.com>.
# All rights reserved.
# vi:ts=4:sw=4:et
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1.  Redistributions of source code must retain the above copyright
#     notice unmodified, this list of conditions, and the following
#     disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
# 3.  Neither the name of Michael Alyn Miller nor the names of the
#     contributors to this software may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""
Convert a tree of Python objects into an XML document using an XSL
template.

The L{toString} function is responsible for transforming one or more
Python objects into an XML document by way of an XSL template.  This
function accepts the same list of Python objects as
L{serialize.toString}, but transforms the serialized Python objects into
an XML file using an XSL template.  C{toString} performs the
serialization step internally, so calling C{serialize.serialize} is not
required.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# Python imports.
import os

# xmlsoft imports.
import libxml2
import libxslt

# sgwf imports.
import serialize



# ######################################################################
# EntityLoader class.
#

class EntityLoader(object):
    """
    libxml2 callback that applies a base path to all absolute stylesheet
    references.  This callback is used by libxml2 when an XSL include or
    import directive is encountered.

    Subclasses can extend this class and override loadFile() if they
    wish to load XSL files from other locations (a database, for
    example).
    """

    # ----------------------------------
    # Constructor and destructor.
    #

    def __init__(self, basePath, relPath):
        """
        Initialize the EntityLoader with the base and relative paths
        that will be used to locate stylesheets.

        @param basePath: The base path that should be used for absolute
            stylesheet references.
        @type basePath: C{str}
        @param relPath: The path that should be used for relative
            stylesheet references.
        @type relPath: C{str}
        """

        # Store the base path and relative path.
        self.__basePath = basePath
        self.__relPath = relPath


    # ----------------------------------
    # EntityLoader methods.
    #

    def loadFile(self, path):
        """
        Load the XSL file with the given path.

        @param path: The path to the XSL file that need to be loaded.
            This path is taken straight from the XSL file and may be
            relative, absolute, or even a URL>
        @type path: C{str}
        @return: The contents of the XSL file, or C{None} if the file
            was not found.
        @rtype: C{str}
        """

        # Create the path the file based on the type of incoming
        # reference (relative or absolute).
        if os.path.isabs(path):
            # Anchor the absolute path at our base path, stripping the
            # initial separator from the incoming path so that we can
            # join() it.
            filePath = os.path.join(self.__basePath, path[1:])
        else:
            # Anchor the relative path, then normalize it.
            filePath = os.path.normpath(os.path.join(self.__relPath, path))

        # Try to open the file.
        try:
            return open(filePath, 'r')
        except IOError:
            # Couldn't find the file; let libxml2 have a go at it.
            return None;


    # ----------------------------------
    # Magic methods.
    #

    def __call__(self, url, id, ctx):
        """libxml2 entity loader callback."""
        return self.loadFile(url)



# ######################################################################
# Transformation functions.
#

def toString(
        xslPath, xslParams=None,
        xslBasePath=None,
        rootTagName='pyxslt',
        encoding='ASCII', prettyPrintXml=False,
        **elements):
    """
    Serialize a dictionary of Python objects to an XML document,
    transform that document using an XSL template, then return the
    textual version of the document.

    @param xslPath: The path to the XSL file that should be used to
        transform the serialized Python objects.
    @type xslPath: C{str} containing the path to an XSL stylesheet.
    @param xslParams: Parameters to pass to the XSL stylesheet.
    @type xslParams: C{dict}
    @param xslBasePath: The path to prepend to absolute stylesheet
        references.
    @type xslBasePath: C{str}
    @param rootTagName: The name of the XML tag that will enclose the
        serialized Python objects.
    @type rootTagName: C{str}
    @param encoding: The character encoding to use when outputting the
        final XML document.  Values such as C{UTF-8}, C{ISO-8859-1},
        C{ASCII}, etc. are appropriate.
    @type encoding: C{str}
    @param prettyPrintXml: C{True} to indent the final XML output,
        C{False} to return the bare XML without any extraneous spaces or
        linefeeds.
    @type prettyPrintXml: C{bool}
    @return: The given Python objects as a transformed XML document.
    @rtype: C{str}
    """

    # Initialize the entity loader if we were given a base path.
    if xslBasePath:
        entityLoader = EntityLoader(xslBasePath, os.getcwd())
        libxml2.setEntityLoader(entityLoader)

    # Load the stylesheet.
    try:
        # Parse the stylesheet.
        xslDoc = libxml2.parseFile(xslPath)
        stylesheet = libxslt.parseStylesheetDoc(xslDoc)
    except:
        # Free the XSL document.
        try: xslDoc.freeDoc()
        except: pass

        # Re-raise the exception.
        raise

    # Render the arguments with the stylesheet.
    try:
        # Create the Serializer.
        ser = serialize.Serializer(rootTagName=rootTagName)

        # Serialize the elements.
        ser.serialize(**elements)

        # Apply the stylesheet to the serialized arguments.
        out = stylesheet.applyStylesheet(ser.xmlDoc, xslParams)

        # Return the rendered content.
        return out.serialize(encoding=encoding, format=prettyPrintXml)
    finally:
        try: out.freeDoc()
        except: pass
        try: stylesheet.freeStylesheet()
        except: pass
        try: doc.freeDoc()
        except: pass



# ######################################################################
# doctest entry point.
#

if __name__ == '__main__':
    import doctest
    doctest.testmod()

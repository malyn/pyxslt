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
Convert a tree of Python objects into an XML document.

Overview
========

    The functions in this module can convert one or more Python objects
    into L{libxml2.xmlDoc} object.  This is performed by the L{toString}
    function, which takes a list of Python objects and returns an XML
    document (wrapped in a C{<pyxslt>..</pyxslt>} tag, although the root
    tag name can be changed).

    All objects given to the serialization function must be able to
    return their value as a string.  pyxslt will iterate through list,
    tuples, and dictionaries.  In addition, pyxslt knows about
    U{SQLObject<http://sqlobject.org/>} instances and will serialize the
    contents of all of the columns in the object.  C{sqlobject.ForeignKey}
    and C{sqlobject.MultipleJoin} references will be traversed as well.

Basic Serialization
===================

    Here is a simple example of encoding a handful of Python
    objects:

        >>> print toString(prettyPrintXml=True,
        ...     firstName='Michael Alyn',
        ...     lastName='Miller',
        ...     oneTwoThree=123,
        ...     myURL='http://www.strangeGizmo.com/',
        ... ),
        <?xml version="1.0" encoding="ASCII"?>
        <pyxslt>
          <last-name>Miller</last-name>
          <my-url>http://www.strangeGizmo.com/</my-url>
          <first-name>Michael Alyn</first-name>
          <one-two-three>123</one-two-three>
        </pyxslt>

    Note that the keyword names (C{firstName}, C{lastName},
    C{oneTwoThree}, etc.) were converted to "XML-style" names
    (C{first-name}, C{last-name}, C{one-two-three}) as part of the
    serialization process.  Complete documentation for this
    transformation can be found in the documentation for the
    L{names.pythonNameToXmlTag} function.

    It should also be pointed out that the serialization process
    does not preserve the order of the Python objects given to the
    C{serialize} function.


Dictionaries
============

    >>> print toString(prettyPrintXml=True,
    ...     foo='bar',
    ...     props={
    ...         'propA': 1,
    ...         'propB': 2,
    ...         'propC': (3, 4, 5),
    ...         'propD': { 'six': 6, 'seven': 7, 'eight': 8 },
    ...     },
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <foo>bar</foo>
      <props>
        <item key="propD">
          <item key="seven">7</item>
          <item key="six">6</item>
          <item key="eight">8</item>
        </item>
        <item key="propA">1</item>
        <item key="propB">2</item>
        <item key="propC">
          <item>3</item>
          <item>4</item>
          <item>5</item>
        </item>
      </props>
    </pyxslt>


Lists and Tuples
================

    >>> print toString(prettyPrintXml=True,
    ...     foo='bar',
    ...     listOfNumbers=(
    ...         1,
    ...         2,
    ...     ),
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <list-of-numbers>
        <item>1</item>
        <item>2</item>
      </list-of-numbers>
      <foo>bar</foo>
    </pyxslt>

pyxslt accepts Python objects as both positional arguments and
keyword arguments.  These objects must contain embedded names so
that pyxslt can create XML tags for those objects.


Complex Serialization
=====================

Complex example:

    >>> class A(object): pass
    ...
    >>> a = A()
    >>> a.foo = 1
    >>> a.bar = 2
    >>> a.baz = [1, 2, 3]
    >>> a.faz = { 'one': 1, 'two': 2, 'three': '1&2' }
    >>> a.b = A()
    >>> a.b.eleven = 11
    >>> a.b.twelve = 12
    >>> firstObj = A()
    >>> firstObj.isFirst = True
    >>> secondObj = A()
    >>> secondObj.isFirst = False
    >>> a.objList = { 'first': firstObj, 'second': secondObj }
    >>> print toString(prettyPrintXml=True,
    ...     myObject=a,
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <my-object>
        <faz>
          <item key="three">1&amp;2</item>
          <item key="two">2</item>
          <item key="one">1</item>
        </faz>
        <b>
          <eleven>11</eleven>
          <twelve>12</twelve>
        </b>
        <bar>2</bar>
        <obj-list>
          <item key="second">
            <is-first>False</is-first>
          </item>
          <item key="first">
            <is-first>True</is-first>
          </item>
        </obj-list>
        <baz>
          <item>1</item>
          <item>2</item>
          <item>3</item>
        </baz>
        <foo>1</foo>
      </my-object>
    </pyxslt>


SQLObject Examples
==================

First we initialize SQLObject and create a few sample tables:

    >>> # Import SQLObject.
    >>> try:
    ...     import pkg_resources
    ...     ignore = pkg_resources.require('SQLObject>=0.7')
    ... except:
    ...     pass
    >>> from sqlobject import *
    ...
    >>> # Create an in-memory SQLite database.
    >>> sqlhub.processConnection = connectionForURI('sqlite:/:memory:')
    ...
    >>> # Define the database classes.
    >>> class Person(SQLObject):
    ...     firstName = StringCol()
    ...     middleInitial = StringCol(length=1, default=None)
    ...     lastName = StringCol()
    ...     website = ForeignKey('URL', default=None)
    ...     phoneNumbers = MultipleJoin('PhoneNumber')
    >>> class PhoneNumber(SQLObject):
    ...     person = ForeignKey('Person')
    ...     phoneType = EnumCol(enumValues=['voice', 'fax', 'cell'])
    ...     countryCode = IntCol(default=1)
    ...     number = StringCol()
    >>> class URL(SQLObject):
    ...     address = StringCol()
    ...
    >>> # Create the tables.
    >>> Person.createTable()
    >>> PhoneNumber.createTable()
    >>> URL.createTable()

Then we create some table entries:

    >>> # Michael Alyn Miller
    >>> malyn = Person(firstName='Michael Alyn', lastName='Miller')
    >>> malyn.website = URL(address='http://www.strangeGizmo.com/')
    >>> mv = PhoneNumber(person=malyn, phoneType='voice', number='555-1212')
    >>> mc = PhoneNumber(person=malyn, phoneType='cell', number='123-4567')
    ...
    >>> # Bob F. Bar
    >>> bob = Person(firstName='Bob', middleInitial='F', lastName='Bar')
    >>> bv = PhoneNumber(person=bob, phoneType='voice', number='262-2620')

Now we serialize the entries:

    >>> print toString(prettyPrintXml=True,
    ...     person=malyn,
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <person id="1">
        <first-name>Michael Alyn</first-name>
        <last-name>Miller</last-name>
        <website id="1">
          <address>http://www.strangeGizmo.com/</address>
        </website>
        <phone-numbers>
          <item id="1">
            <phone-type>voice</phone-type>
            <country-code>1</country-code>
            <number>555-1212</number>
          </item>
          <item id="2">
            <phone-type>cell</phone-type>
            <country-code>1</country-code>
            <number>123-4567</number>
          </item>
        </phone-numbers>
      </person>
    </pyxslt>

Notice that the Person table is included when a PhoneNumber is
serialized directly (rather than as a MultipleJoin from a Person
object):

    >>> print toString(prettyPrintXml=True,
    ...     phoneNumber=mv,
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <phone-number id="1">
        <person id="1">
          <first-name>Michael Alyn</first-name>
          <last-name>Miller</last-name>
          <website id="1">
            <address>http://www.strangeGizmo.com/</address>
          </website>
          <phone-numbers>
            <item id="1">
              <phone-type>voice</phone-type>
              <country-code>1</country-code>
              <number>555-1212</number>
            </item>
            <item id="2">
              <phone-type>cell</phone-type>
              <country-code>1</country-code>
              <number>123-4567</number>
            </item>
          </phone-numbers>
        </person>
        <phone-type>voice</phone-type>
        <country-code>1</country-code>
        <number>555-1212</number>
      </phone-number>
    </pyxslt>

This behavior is not always desired and could result in a large
number of returned, serialized rows.  To exclude one or more SQL
relationship from the serialized result, pass a list of C{(dbClass,
attrName)} tuples to the C{ignoreRelationship} keyword argument:

    >>> print toString(prettyPrintXml=True,
    ...     ignoreRelationship=[(PhoneNumber, 'person')],
    ...     phoneNumber=mv,
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <phone-number id="1">
        <person>1</person>
        <phone-type>voice</phone-type>
        <country-code>1</country-code>
        <number>555-1212</number>
      </phone-number>
    </pyxslt>

This functionality can also be used if you want to output the
results of an SQLObject query, but do not want to descend into a
specific MultipleJoin:

    >>> print toString(prettyPrintXml=True,
    ...     ignoreRelationship=[(Person, 'phoneNumbers')],
    ...     phoneList=Person.select(),
    ... ),
    <?xml version="1.0" encoding="ASCII"?>
    <pyxslt>
      <phone-list>
        <item id="1">
          <first-name>Michael Alyn</first-name>
          <last-name>Miller</last-name>
          <website id="1">
            <address>http://www.strangeGizmo.com/</address>
          </website>
        </item>
        <item id="2">
          <first-name>Bob</first-name>
          <middle-initial>F</middle-initial>
          <last-name>Bar</last-name>
        </item>
      </phone-list>
    </pyxslt>

Note that ignored MultipleJoin relationship do not appear at all in
the output tree, whereas ignored ForeignKey relationships will
include a node containing the id of the related row.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# xmlsoft imports.
import libxml2

# pyxslt imports.
import names



# ######################################################################
# Serializer class.
#

class Serializer(object):
    """
    Serializes Python objects to XML documents.

    @ivar rootTagName: The name of the root tag in the XML document that
        will be created during the serialization process.
    @type rootTagName: C{str}
    @ivar ignoreRelationship: A list of I{className, propName} tuples
        that describe properties that should not be serialized.  These
        properties will be skipped during the serialization process and
        will not appear in their parent's output tree.  Note that, if
        the elided property is itself an object and that object has an
        'id' property, then a reference to the elided object will be
        inserted.  This is most commonly seen in the case of a
        C{sqlobject.ForeignKey} relationship.
    @type ignoreRelationship: C{list} of I{className, propName}
        tuples
    @ivar xmlDoc: The XML document that contains the contents of the
        most-recently serialized set of Python objects.  This object
        will be freed by the C{Serializer} class as soon as a new call
        to L{serialize} or L{serializeOne} is made.  B{Do not} cache
        this object and B{do not} free it.  Most users of the
        C{Serializer} class should call L{toXmlDoc} to obtain a copy of
        the L{xmlDoc} object instead of accessing the property directly.
    @type xmlDoc: L{libxml2.xmlDoc}
    @ivar _rootNode: The root node of the current XML document.
    @type _rootNode: L{libxml2.xmlNode}
    """

    # ######################################
    # Constructor and destructor.
    #

    def __init__(self, rootTagName='pyxslt', ignoreRelationship=[]):
        """
        Create a Serializer object that can be used to serialize one or
        more sets of Python elements.

        @param rootTagName: The name of the root tag in the XML document
            that will be created during the serialization process.
        @type rootTagName: C{str}
        @param ignoreRelationship: A list of I{className, propName}
            tuples that describe properties that should not be
            serialized.  These properties will be skipped during the
            serialization process and will not appear in their parent's
            output tree.  Note that, if the elided property is itself an
            object and that object has an 'id' property, then a
            reference to the elided object will be inserted.  This is
            most commonly seen in the case of a C{sqlobject.ForeignKey}
            relationship.
        @type ignoreRelationship: C{list} of I{className, propName}
            tuples
        """

        # Store the configuration properties.
        self.rootTagName = rootTagName
        self.ignoreRelationship = ignoreRelationship

        # Initialize our internal properties.
        self.xmlDoc = None

    def __del__(self):
        """
        Free the memory used by the Serializer object.
        """

        # Free the XML document.
        self._freeXmlDoc()



    # ######################################
    # xmlDoc object management.
    #

    def _createXmlDoc(self):
        """
        Create a new L{libxml2.xmlDoc} object and store it in the
        L{xmlDoc} property.  The root node (with the name L{rootTagName}
        will be created and added to the document.  If the Serializer
        class already has an active L{xmlDoc} object, then that object
        will be freed before the new one is created.
        """

        # Free the current XML document.
        self._freeXmlDoc()

        # Create the XML document.
        self.xmlDoc = libxml2.newDoc('1.0')

        # Create the root node and add it to the document.
        self._rootNode = libxml2.newNode(self.rootTagName)
        self.xmlDoc.setRootElement(self._rootNode)

    def _freeXmlDoc(self):
        """
        Free the current L{xmlDoc}, if one exists.
        """

        # Free the current XML document if necessary.
        if self.xmlDoc:
            self.xmlDoc.freeDoc()
            self.xmlDoc = None



    # ######################################
    # Serialization methods.
    #

    def serialize(self, **elements):
        """
        Serialize one or more Python objects.  This method only accepts
        keyword arguments.  Each value in the argument dictionary will
        be serialized into the document under a tag with the name of the
        keyword.
        """

        # Create a new document.
        self._createXmlDoc()

        # Initialize the node stack.
        self.__nodeStack = []

        # Serialize all of the elements.
        for objName, obj in elements.items():
            self._serializeObject(self._rootNode, objName, obj)

    def serializeOne(self, element):
        """
        Serialize a single Python object directly under the root node.
        Unlike the L{serialize} method, C{serializeOne} will not wrap
        the serialized object in an enclosing tag (other than the root
        tag).
        """

        # Create a new document.
        self._createXmlDoc()

        # Initialize the node stack.
        self.__nodeStack = []

        # Serialize the element.
        self._serializeItem(self._rootNode, element)



    # ######################################
    # Internal serialization methods.
    #

    def _serializeObject(self, parentNode, objName, obj):
        # Convert the object name to an XML tag name.
        tagName = names.pythonNameToXmlTag(objName)

        # Ignore empty objects.
        if obj is None:
            return

        # Create the node for this object.
        node = parentNode.newChild(None, tagName, None)

        # Serialize the object.
        self._serializeItem(node, obj)


    def _serializeItem(self, parentNode, obj):
        # Serialize the object based on its type.
        objType = type(obj)
        if         objType == list \
                or objType == tuple \
                or obj.__class__.__name__ == 'SelectResults':
            self._serializeList(parentNode, obj)

        elif objType == dict:
            self._serializeDict(parentNode, obj)

        elif hasattr(obj, 'sqlmeta'): # an SQLObject
            self._serializeSqlObject(parentNode, obj)

        elif hasattr(obj, '__dict__'): # a normal object
            for objName, obj in obj.__dict__.items():
                self._serializeObject(parentNode, objName, obj)

        else:
            parentNode.addContent(str(obj))


    def _serializeDict(self, parentNode, element):
        # Serialize each entry in the dictionary.
        for key, value in element.items():
            # Create the node for this item.
            itemNode = parentNode.newChild(None, 'item', None)

            # Add the key to the item node.
            itemNode.newProp('key', str(key))

            # Serialize the item.
            self._serializeItem(itemNode, value)


    def _serializeList(self, parentNode, element):
        # Serialize each entry in the list.
        for item in element:
            # Create the node for this item.
            itemNode = parentNode.newChild(None, 'item', None)

            # Serialize the item.
            self._serializeItem(itemNode, item)


    def _serializeSqlObject(self, parentNode, sqlObj):
        # Add the 'id' attribute to the parent node.
        parentNode.newProp('id', str(sqlObj.id))

        # Add this object to the node stack.
        self.__nodeStack.append(sqlObj)

        # Serialize each column.
        for column in sqlObj.sqlmeta.columnList:
            # Retrieve the name, type, and value of the column.
            colName = column.origName
            colType = type(column)
            colValue = getattr(sqlObj, colName)

            # Get the tag name.
            colTagName = names.pythonNameToXmlTag(colName)

            # Ignore empty columns.
            if colValue is None:
                continue

            # Serialize the object based on its type.
            if column.foreignKey:
                # Do not descend into ignored relationships.  Instead, just
                # output the id of the related column.
                if (sqlObj.sqlmeta.soClass, colName) in self.ignoreRelationship:
                    parentNode.newTextChild(None, colTagName, str(colValue.id))
                    continue

                # Only traverse the foreign key if it is not already in
                # our node stack.  This is used to avoid an SQLObject ->
                # MultipleJoin -> ForeignKey -> MultipleJoin -> ... loop).
                if colValue not in self.__nodeStack:
                    node = parentNode.newChild(None, colTagName, None)
                    self._serializeSqlObject(node, colValue)
            elif column.__class__.__name__ == 'SODateTimeCol':
                parentNode.newTextChild(None, colTagName, colValue.isoformat())
            else:
                parentNode.newTextChild(None, colTagName, str(colValue))

        # Serialize each join.
        for join in sqlObj.sqlmeta.joins:
            # Ignore this join if requested to do so.
            if (sqlObj.sqlmeta.soClass, join.joinMethodName) in self.ignoreRelationship:
                continue

            # Create the join node.
            joinNode = parentNode.newChild(
                None, names.pythonNameToXmlTag(join.joinMethodName), None)

            # Add the entries from the joined table.  Do not process the
            # ForeignKey entry in the joined table that points back to this
            # table.
            for joinedRow in getattr(sqlObj, join.joinMethodName):
                itemNode = joinNode.newChild(None, 'item', None)
                self._serializeSqlObject(itemNode, joinedRow)

        # Remove this object from the node stack.
        self.__nodeStack.pop()



    # ######################################
    # Conversion methods.
    #

    def toXmlDoc(self):
        """
        Return a (copy of) the L{libxml2.xmlDoc} that contains the
        contents of the most-recently serialized set of Python objects.
        It is the responsibility of the caller to free this document.

        @return: The XML document that contains the contents of the
            most-recently serialized set of Python objects.  This object
            must be freed by the caller.
        @rtype: L{libxml2.xmlDoc}
        """

        # Make a copy of the original document.
        xmlDocCopy = libxml2.newDoc('1.0')
        rootNodeCopy = self._rootNode.docCopyNode(xmlDocCopy, True)
        xmlDocCopy.setRootElement(rootNodeCopy)

        # Return the copy of the document.
        return xmlDocCopy

    def toString(self, encoding='ASCII', prettyPrintXml=False):
        """
        Return the textual version of the XML document that contains the
        most-recently serialized set of Python objects.

        @return: The most-recently serialized Python objects as an XML
            document.
        @rtype: C{str}
        """

        # Serialize the document to a string and return the string.
        return self.xmlDoc.serialize(
            encoding=encoding,
            format=prettyPrintXml)



    # ######################################
    # Python special methods.
    #

    def __str__(self):
        return self.toString()



# ######################################################################
# Serialization functions.
#

def toString(
        rootTagName='pyxslt',
        encoding='ASCII', prettyPrintXml=False,
        ignoreRelationship=[],
        **elements):
    """
    Serialize a dictionary of Python objects to an XML document and
    return the textual version of the document.

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
    @return: The given Python objects as an XML document.
    @rtype: C{str}
    """

    # Create the Serializer.
    ser = Serializer(
        rootTagName=rootTagName,
        ignoreRelationship=ignoreRelationship)

    # Serialize the elements.
    ser.serialize(**elements)

    # Return the serialized XML document as a string.
    return ser.toString(encoding, prettyPrintXml)



# ######################################################################
# doctest entry point.
#

if __name__ == '__main__':
    import doctest
    doctest.testmod()

========================================================================
pyxslt
========================================================================


Overview
========================================================================

pyxslt makes it easy to turn Python objects into XML documents.  In
addition to basic XML serialization, pyxslt can also apply an XSL
stylesheet to the serialized XML fragments.  You could, for example, use
pyxslt to convert the results of an SQLObject_ query to an XHTML file.

All Python objects given to pyxslt are converted into their string
representations.  pyxslt focuses on serializing objects in such a way as
to make the construction of XSL stylesheets as easy as possible.  As a
result, pyxslt's XML serialization is usually not reversible.

See the `pyxslt product page`_ on the strangeGizmo.com site for more
information.

.. _SQLObject: http://sqlobject.org/
.. _pyxslt product page: http://www.strangeGizmo.com/products/pyxslt/



Change List
========================================================================

0.9.1
-----

-   SQLObject DateTimeCol values are now serialized as ISO 8601 values
    using ``isoformat()`` instead of just being converted to strings.
    ISO 8601 values are easier to use with the various XSLT date
    functions.

-   Add the ``README.txt`` file.


0.9.0
-----

-   Initial release.

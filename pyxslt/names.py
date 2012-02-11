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
Convert Python class and property names to valid XML tag names.

This module is used by the L{serialize} module as part of the object
serialization process.  The only real function of interest is
L{pythonNameToXmlTag}, which converts a Python class or attribute name
to an XML tag name.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# Python imports.
import re



# ######################################################################
# Name checking.
#

_badNameRegExp = re.compile('[^A-Za-z0-9]')

def _checkName(name):
    """
    Check a name to make sure that it can be turned into a valid XML
    tag.  Only letters and numbers are allowed in a (tag) name.

    Examples of valid names:

        >>> _checkName('abc123')
        True
        >>> _checkName('abcAbc')
        True
        >>> _checkName('abcDefGhiJkl')
        True

    Example of invalid names:

        >>> _checkName('ab&c')
        False
        >>> _checkName('ab-c')
        False
        >>> _checkName('ab c')
        False
    """

    return _badNameRegExp.search(name) is None



# ######################################################################
# Acronym repair.
#

_acronymRegExp = re.compile(
    r'(?:'
        r'(?P<acronym>[A-Z]+)'  # Acronym
        r'(?P<nextWord>'        # and..
            r'([A-Z][a-z])'         # the beginning of a Bumpy word
            r'|'                    # or
            r'$'                    # the end of the string.
        r')'
    r')')

def _fixAcronyms(s):
    """
    Convert embedded acronyms to bumpyCaps acronyms (i.e.: ABC -> Abc).

    Single acronyms inside of the string will have all of the letters
    after their first letter converted to lowercase:

        >>> _fixAcronyms('myURL')
        'myUrl'
        >>> _fixAcronyms('myURLIsHere')
        'myUrlIsHere'
        >>> _fixAcronyms('URLInfo')
        'UrlInfo'

    Input strings that are only an acronym will be fixed as well.:

        >>> _fixAcronyms('URL')
        'Url'

    Multiple acronyms are properly handled:

        >>> _fixAcronyms('oneURLAndAnotherURL')
        'oneUrlAndAnotherUrl'

    Single-letter acronyms at the end of the string are O.K. as well:

        >>> _fixAcronyms('exhibitA')
        'exhibitA'
    """

    return _acronymRegExp.sub(__acronymRepl, s)

def __acronymRepl(match):
    acronym = match.group('acronym')
    nextWord = match.group('nextWord')
    return '%s%s%s' % (acronym[0], acronym[1:].lower(), nextWord)



# ######################################################################
# Hyphenation.
#

_hyphenRegExp = re.compile(
    r'[a-z]'    # End of the previous word and
    r'[A-Z]')   # the start of the next Bumpy word.

def _insertHyphens(s):
    """
    Turn a bumpyCaps-separated word into a lowercase, hyphen-separated
    word.  Acronyms must be in bumpyCaps or this routine will return
    unexpected results.

    Individual words in a bumpyCaps string will be separated by hyphens:

        >>> _insertHyphens('thisIsMyString')
        'this-is-my-string'
        >>> _insertHyphens('FirstLetterCanBeCaps')
        'first-letter-can-be-caps'

    Single words are properly handled:

        >>> _insertHyphens('word')
        'word'
        >>> _insertHyphens('Word')
        'word'

    Single-letter words at the end of the string are O.K. as well:

        >>> _insertHyphens('exhibitA')
        'exhibit-a'
    """

    return _hyphenRegExp.sub(__hyphenRepl, s).lower()

def __hyphenRepl(match):
    s = match.group(0).lower()
    return '%s-%s' % (s[0], s[1:])



# ######################################################################
# Name conversion.
#

def pythonNameToXmlTag(pythonName):
    """
    Convert a bumpyCase name to a hyphenated-tag name.

    Each word in the Python name should begin with a capital letter.
    The first word may be either lowercase or uppercase:

        >>> pythonNameToXmlTag('attributeName')
        'attribute-name'
        >>> pythonNameToXmlTag('ClassName')
        'class-name'

    Words with all capital letters (i.e.: acronyms) will be properly
    separated:

        >>> pythonNameToXmlTag('IPAddress')
        'ip-address'
        >>> pythonNameToXmlTag('aURL')
        'a-url'
        >>> pythonNameToXmlTag('thisURLAndStuff')
        'this-url-and-stuff'

    Single words will not be transformed:

        >>> pythonNameToXmlTag('attribute')
        'attribute'

    Unless they are entirely in uppercase, in which case they will be
    converted to lowercase:

        >>> pythonNameToXmlTag('URL')
        'url'

    Multiple acronyms are properly handled:

        >>> pythonNameToXmlTag('oneURLAndAnotherURLAndAnother')
        'one-url-and-another-url-and-another'

    Single-letter words at the end of the string are O.K. as well:

        >>> pythonNameToXmlTag('exhibitA')
        'exhibit-a'
    """

    # Make sure that pythonName consists solely of alphanumeric
    # characters.  No spaces and no punctuation.
    if not _checkName(pythonName):
        raise ValueError, \
            'Name "%s" is invalid: only letters and numbers are allowed' % (
                pythonName)

    # Fix acronyms.
    fixedPythonName = _fixAcronyms(pythonName)

    # Put in hyphens.
    xmlTag = _insertHyphens(fixedPythonName)

    # Return the XML tag.
    return xmlTag



# ######################################################################
# doctest entry point.
#

if __name__ == '__main__':
    import doctest
    doctest.testmod()

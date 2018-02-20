.. module:: urlparse

********
Urlparse
********

This module defines a standard interface to break Uniform Resource Locator (URL)
strings up in components (addressing scheme, network location, path etc.)


    
.. function:: parse(url)

   Returns a tuple (*scheme*, *netloc*, *path*, *query*, *fragment*) derived from *url*.

   This corresponds to the general structure of a URL: ``scheme://netloc/path?query#fragment``.
   Each tuple item is a string, possibly empty. The components are not broken up in
   smaller parts (for example, the network location is a single string), and %
   escapes are not expanded. The delimiters as shown above are not part of the
   result, except for a leading slash in the *path* component, which is retained if
   present.  For example:

      import urlparse
      o = urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
      
      # result is ('http', 'www.cwi.nl:80', '/%7Eguido/Python.html', '', '')
      

   Following the syntax specifications in :rfc:`1808`, urlparse recognizes
   a netloc only if it is properly introduced by '//'.  Otherwise the
   input is presumed to be a relative URL and thus to start with
   a path component.

    
.. function:: parse_netloc(netloc)

    Given *netloc* as parsed by :func:`.parse`, breaks it in its component returning a tuple (*user*, *password*, *host*, *port*).
    Each component of the returned tuple is a string.

    
.. function:: quote(s)

    Return the urlencoded version of *s*.

    Urlencoding transforms unsafe bytes to their %XX representation where XX is the hex value of the byte.

    Safe bytes are:

        * lowercase letters from "a" to "z" (bytes from 0x61 to 0x7a)
        * uppercase letters from "A" to "Z" (bytes from 0x41 to 0x5a)
        * numbers from "0" to "9" (bytes from 0x30 to 0x39)
        * the following symbols: $-_.+!*'()

    
.. function:: quote_plus(s)

    Like :func:`quote`, but also escapes :code:`+` symbol.
    
.. function:: unquote(s)

    If *s* is urlencoded, returns *s* with every ``+`` substituted with a space and every ``%xx`` substituted with the corresponding character.

    
.. function:: parse_qs(qs)

    Parses a query string *qs* and returns a dictionary containing the association between keys and values of *qs*.
    Values are urldecoded by :func:`unquote`.
    
    
.. function:: urlencode(data)

    Tranforms data dictionary in a urlencoded query string and returns the query string.
    Each pair (key, value) is encoded by *quote_via* function.
    By default, :func:`quote_plus` is used to quote the values.
    An alternate function that can be passed as quote_via is :func:`quote`.
    
    

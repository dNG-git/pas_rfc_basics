# -*- coding: utf-8 -*-

"""
RFC basics for Python
Easy to use and RFC compliant methods
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?py;rfc_basics

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(rfcBasicsVersion)#
#echo(__FILEPATH__)#
"""

import re

from .basics import Basics

class Header(Basics):
    """
Parses RFC 7231 compliant headers.

:author:    direct Netware Group
:copyright: (C) direct Netware Group - All rights reserved
:package:   rfc_basics.py
:since:     v0.1.00
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
    """

    RE_HEADER_FIELD_ESCAPED = re.compile("(\\\\+)$")
    """
RegExp to find escape characters
    """

    @staticmethod
    def _find_field_list_end_position(data, position, end_char):
        """
Find the position of the given character.

:param data: Data
:param position: Position offset
:param end_char: Character

:return: (str) List containing str or dict if a field name was identified;
         False on error
:since:  v0.1.00
        """

        next_position = position
        _return = -1

        while (end_char is not None):
            next_position = data.find(end_char, 1 + next_position)
            re_result = (None if (next_position < 1) else Header.RE_HEADER_FIELD_ESCAPED.search(data[position:next_position]))

            if (next_position < 1): break
            elif (re_result is None or (len(re_result.group(1)) % 2) == 0):
                _return = 1 + next_position
                break
            #
        #

        return _return
    #

    @staticmethod
    def get_field_list_dict(field_list, separator = ",", field_separator = ":"):
        """
Returns a RFC 7231 compliant list of fields from a header message.

:param field: Header field list
:param separator: Separator between fields
:param field_separator: Separator between key-value pairs; None to not parse it

:return: (list) List containing str or dict if a field name was identified
:since:  v0.1.00
        """

        _return = [ ]

        fields = [ ]
        last_position = 0
        field_list_length = (len(field_list) if (isinstance(field_list, str)) else 0)

        while (last_position < field_list_length):
            separator_position = field_list.find(separator, last_position)
            quotation_mark_position = field_list.find('"', last_position)
            next_position = -1

            if (separator_position > -1): next_position = separator_position

            if (quotation_mark_position > -1
                and (next_position < 0 or next_position > quotation_mark_position)
               ): next_position = Header._find_field_list_end_position(field_list, quotation_mark_position, '"')

            if (next_position < 0):
                fields.append(field_list[last_position:])
                break
            else:
                fields.append(field_list[last_position:next_position])
                if (field_list[next_position:1 + next_position] == separator): next_position += 1
                last_position = next_position
            #
        #

        for field in fields:
            if (field_separator is not None and field_separator in field):
                field = field.split(field_separator, 1)
                field_value = field[1]

                field_value = (field_value[1:-1]
                               if (field_value[:1] == '"' and field_value[-1:] == '"') else
                               field_value.strip()
                              )

                field = { "key": field[0].strip(), "value": field_value }
            else: field = field.strip()

            _return.append(field)
        #

        return _return
    #
#

# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;rfc_basics

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasRfcBasicsVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error,invalid-name

from calendar import timegm
from datetime import datetime
import re
import time

try: from pytz import timezone
except ImportError: timezone = None

class DateTime(object):
    """
This class provides basic functions to handle date and time related RFCs.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: rfc_basics
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    RFC850_DAYS = [ "Monday", "Tuesday", "Wednesday‎", "Thursday‎", "Friday", "Saturday‎", "Sunday" ]
    """
RFC 5322 day names
    """
    RFC5322_DAYS = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]
    """
RFC 5322 day names
    """
    RFC5322_MONTHS = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
    """
RFC 5322 month names
    """

    @staticmethod
    def get_iso8601_datetime(timestamp, date = True, _time = True):
        """
Returns the ISO-8601 compliant date and time for an UNIX timestamp. Please
note that timezone names can only be handled if pytz is available.

:param timestamp: UNIX timestamp

:return: (str) ISO-8601 compliant date and / or time
:since:  v1.0.0
        """

        time_struct = time.gmtime(timestamp)

        _return = (time.strftime("%Y-%m-%d", time_struct) if (date) else "")
        if (_time): _return += time.strftime(("T%H:%M:%S" if (date) else "%H:%M:%S"), time_struct)

        return _return
    #

    @staticmethod
    def get_iso8601_timestamp(value, date = True, has_time = True, has_timezone = True, current_day = True):
        """
Returns the UNIX timestamp for a ISO-8601 compliant date and time. Please
note that timezone names can only be handled if pytz is available.

:param value: ISO-8601 compliant date and / or time

:return: (int) UNIX timestamp
:since:  v1.0.0
        """

        if (current_day and (not date)):
            time_struct = time.gmtime()

            year = str(time_struct.tm_year)
            month = str(time_struct.tm_mon)
            day = str(time_struct.tm_mday)
        else:
            year = "1970"
            month = "01"
            day = "01"
        #

        hours = "00"
        minutes = "00"
        offset = 0
        operator = 1
        seconds = "00"
        time_data = ""
        time_format = ""
        timezone_offset = 0
        value_length = len(value)
        weeks_offset = 0

        if (date):
            char = value[:1]

            if (char == "+" or char == "-"):
                offset = 1
                operator = (-1 if (char == "-") else 1)
                year = value[1:5]
            else:
                offset = 0
                year = value[:4]
            #

            if (5 + offset < value_length):
                char = value[4 + offset:5 + offset]

                if (char == "-"):
                    char = value[5 + offset:6 + offset]
                    offset += 1
                #

                if (char == "W" and 6 + offset < value_length): weeks_offset = 604800 * int(value[5 + offset:7 + offset])
                else: month = value[4 + offset:6 + offset]
            #

            if (7 + offset < value_length):
                char = value[6 + offset:7 + offset]
                if (char == "-"): offset += 1
                day = value[6 + offset:8 + offset]
            #

            offset += 8
        #

        if (has_time and 7 + offset < value_length and (offset < 1 or value[offset:1 + offset] == "T")):
            if (offset > 0): offset += 1

            hours = value[offset:2 + offset]
            minutes = value[3 + offset:5 + offset]
            seconds = value[6 + offset:8 + offset]
            time_data = "{0}{1}{2}".format(hours, minutes, seconds)
            time_format = "%H%M%S"

            _datetime = datetime.strptime("{0}{1}{2}{3}".format(year, month, day, time_data), "%Y%m%d{0}".format(time_format))

            if (has_timezone and 8 + offset < value_length):
                timezone_value = value[8 + offset:]

                if (":" in timezone_value):
                    timezone_value = timezone_value.split(":", 1)
                    timezone_offset = (-3600 * int(timezone_value[0])) + (60 * int(timezone_value[1]))
                elif (timezone is None): raise RuntimeError("Timezone names are only available if pytz is available")
                else: timezone_offset = -1 * timezone(timezone_value).utcoffset(_datetime).total_seconds()
            #
        else: _datetime = datetime.strptime("{0}{1}{2}".format(year, month, day), "%Y%m%d")

        return operator * int((_datetime.utctimestamp() if (hasattr(_datetime, "utctimestamp")) else timegm(_datetime.timetuple())) + weeks_offset + timezone_offset)
    #

    @staticmethod
    def get_rfc5322_datetime(timestamp):
        """
Returns a RFC 5322 compliant date and time.

:param timestamp: UNIX timestamp

:return: (str) RFC 5322 compliant date and time
:since:  v1.0.0
        """

        time_struct = time.gmtime(timestamp)
        _return = time.strftime("%%a, %d %%b %Y %H:%M:%S GMT", time_struct)
        _return = _return.replace("%a", DateTime.RFC5322_DAYS[time_struct.tm_wday], 1)
        _return = _return.replace("%b", DateTime.RFC5322_MONTHS[time_struct.tm_mon - 1], 1)

        return _return
    #

    @staticmethod
    def get_rfc5322_timestamp(_datetime):
        """
Returns the UNIX timestamp for a RFC 5322 compliant date and time.

:param _datetime: RFC 5322 compliant date and time

:return: (int) UNIX timestamp
:since:  v1.0.0
        """

        re_result = re.match("(\\w{3}, )*(\\d{1,2}) (\\w{3}) (\\d{2,4}) (\\d{1,2}):(\\d{1,2}):(\\d{1,2}) (\\w{3}|[+\\-]\\d{1,2}:\\d{1,2})$", _datetime)
        if (re_result is None): raise ValueError("Given date and time is not RFC 5322 compliant formatted")

        mon = 1 + DateTime.RFC5322_MONTHS.index(re_result.group(3))

        timezone_format = ("%z" if (":" in re_result.group(7)) else ("%Z"))

        if (re_result.group(1) is None):
            time_struct = time.strptime("{0} {1:0=2d} {2} {3}:{4}:{5} {6}".format(re_result.group(2),
                                                                                  mon,
                                                                                  re_result.group(4),
                                                                                  re_result.group(5),
                                                                                  re_result.group(6),
                                                                                  re_result.group(7),
                                                                                  re_result.group(8)
                                                                                 ),
                                        "%d %m %Y %H:%M:%S " + timezone_format
                                       )
        else:
            wday = DateTime.RFC5322_DAYS.index(re_result.group(1)[:-2])
            wday = (0 if (wday > 5) else 1 + wday)

            time_struct = time.strptime("{0}, {1} {2:0=2d} {3} {4}:{5}:{6} {7}".format(wday,
                                                                                       re_result.group(2),
                                                                                       mon,
                                                                                       re_result.group(4),
                                                                                       re_result.group(5),
                                                                                       re_result.group(6),
                                                                                       re_result.group(7),
                                                                                       re_result.group(8)
                                                                                      ),
                                        "%w, %d %m %Y %H:%M:%S " + timezone_format
                                       )
        #

        return timegm(time_struct)
    #

    @staticmethod
    def get_rfc7231_timestamp(_datetime):
        """
Returns the UNIX timestamp for a RFC 7231 compliant date and time.

:param _datetime: RFC 7231 compliant date and time

:return: (int) UNIX timestamp
:since:  v1.0.0
        """

        # pylint: disable=broad-except

        _return = None

        try: _return = DateTime.get_rfc5322_timestamp(_datetime)
        except Exception: pass

        if (_return is None): # RFC 850
            re_result = re.match("(\\w{6,9}), (\\d{1,2})-(\\w{3})-(\\d{2}) (\\d{1,2}):(\\d{1,2}):(\\d{1,2}) (\\w{3}|[+\\-]\\d{1,2}:\\d{1,2})$", _datetime)

            if (re_result is not None):
                wday = DateTime.RFC850_DAYS.index(re_result.group(1))
                wday = (0 if (wday > 5) else 1 + wday)

                mon = 1 + DateTime.RFC5322_MONTHS.index(re_result.group(3))

                timezone_format = ("%z" if (":" in re_result.group(7)) else ("%Z"))
                _return = timegm(time.strptime("{0:d}, {1} {2:0=2d} {3} {4}:{5}:{6} {7}".format(wday, re_result.group(2), mon, re_result.group(4), re_result.group(5), re_result.group(6), re_result.group(7), re_result.group(8)), "%w, %d %m %y %H:%M:%S " + timezone_format))
            #
        #

        if (_return is None): # ANSI C
            try: _return = timegm(time.strptime(_datetime))
            except Exception: pass
        #

        if (_return is None): raise ValueError("Given date and time is not RFC 7231 compliant formatted")
        return _return
    #
#

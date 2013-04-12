# -*- coding: utf-8 -*-
##j## BOF

"""
RFC Basics for Python
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?py;rfc_basics

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(rfcBasicsVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from calendar import timegm
import re, time

try: _unicode_object = { "type": unicode, "str": unicode.encode }
except: _unicode_object = { "type": bytes, "str": bytes.decode }

class direct_basics(object):
#
	"""
This class provides basic functions described in different RFCs.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    rfc_basics.py
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	RE_HEADER_FOLDED_LINE = re.compile("\\r\\n((\\x09)(\\x09)*|(\\x20)(\\x20)*)(\\S)")
	"""
Regular expression to find folded lines
	"""
	RFC850_DAYS = [ "Monday", "Tuesday", "Wednesday‎", "Thursday‎", "Friday", "Saturday‎", "Sunday" ]
	"""
RFC 1123 day names
	"""
	RFC1123_DAYS = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]
	"""
RFC 1123 day names
	"""
	RFC1123_MONTHS = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
	"""
RFC 1123 month names
	"""

	@staticmethod
	def get_headers(data):
	#
		"""
Parses a string of headers.

:param data: String of headers

:return: (dict) Dict with parsed headers; False on error
:since:  v0.1.00
		"""

		global _unicode_object
		var_return = False

		if (data == _unicode_object['type']): data = _unicode_object['str'](data, "utf-8")

		if (type(data) == str and len(data) > 0):
		#
			data = direct_basics.RE_HEADER_FOLDED_LINE.sub("\\2\\4\\6", data)
			var_return = { }

			headers = data.split("\r\n")

			for header_line in headers:
			#
				header = header_line.split(":", 1)

				if (len(header) == 2):
				#
					header_name = header[0].strip().lower().replace("-", "_")
					header[1] = header[1].strip()

					if (header_name in var_return):
					#
						if (type(var_return[header_name]) == list): var_return[header_name].append(header[1])
						else: var_return[header_name] = [ var_return[header_name], header[1] ]
					#
					else: var_return[header_name] = header[1]
				#
				elif (len(header[0]) > 0):
				#
					if ("@nameless" in var_return): var_return['@nameless'] += "\n" + header[0].strip()
					else: var_return['@nameless'] = header[0].strip()
				#
			#
		#

		return var_return
	#

	@staticmethod
	def get_rfc1123_datetime(timestamp):
	#
		"""
Returns a RFC 1123 compliant date and time.

:param timestamp: UNIX timestamp

:access: protected
:return: (str) RFC 1123 compliant date and time
:since:  v0.1.00
		"""

		time_struct = time.gmtime(timestamp)
		var_return = time.strftime("%%a, %d %%b %Y %H:%M:%S GMT", time_struct)
		var_return = var_return.replace("%a", direct_basics.RFC1123_DAYS[time_struct.tm_wday], 1)
		var_return = var_return.replace("%b", direct_basics.RFC1123_MONTHS[time_struct.tm_mon - 1], 1)

		return var_return
	#

	@staticmethod
	def get_rfc1123_timestamp(datetime):
	#
		"""
Returns a RFC 1123 compliant date and time.

:param datetime: RFC 1123 compliant date and time

:access: protected
:return: (int) UNIX timestamp
:since:  v0.1.00
		"""

		re_result = re.match("(\w{3}), (\d{1,2}) (\w{3}) (\d{2,4}) (\d{1,2}):(\d{1,2}):(\d{1,2}) (\w{3}|[+-]\d{1,2}:\d{1,2})$", datetime)
		if (re_result == None): raise ValueError("Given date and time is not RFC 1123 compliant formatted", 38)

		mon = direct_basics.RFC1123_MONTHS.index(re_result.group(3))
		mon = ("0{0:d}".format(1 + mon) if (mon < 9) else str(1 + mon))

		wday = direct_basics.RFC1123_DAYS.index(re_result.group(1))
		wday = (0 if (wday > 5) else 1 + wday)

		timezone_format = ("%z" if (":" in re_result.group(7)) else ("%Z"))
		return timegm(time.strptime("{0:d}, {1} {2} {3} {4}:{5}:{6} {7}".format(wday, re_result.group(2), mon, re_result.group(4), re_result.group(5), re_result.group(6), re_result.group(7), re_result.group(8)), "%w, %d %m %Y %H:%M:%S " + timezone_format))
	#

	@staticmethod
	def get_rfc2616_timestamp(datetime):
	#
		"""
Returns a RFC 2616 compliant date and time.

:param datetime: RFC 2616 compliant date and time

:access: protected
:return: (int) UNIX timestamp
:since:  v0.1.00
		"""

		var_return = None

		try: var_return = direct_basics.get_rfc1123_timestamp(datetime)
		except: pass

		if (var_return == None): # RFC 850
		#
			re_result = re.match("(\w{6,9}), (\d{1,2})-(\w{3})-(\d{2}) (\d{1,2}):(\d{1,2}):(\d{1,2}) (\w{3}|[+-]\d{1,2}:\d{1,2})$", datetime, re.I)

			if (re_result != None):
			#
				mon = direct_basics.RFC1123_MONTHS.index(re_result.group(3))
				mon = ("0{0:d}".format(1 + mon) if (mon < 9) else str(1 + mon))

				wday = direct_basics.RFC850_DAYS.index(re_result.group(1))
				wday = (0 if (wday > 5) else 1 + wday)

				timezone_format = ("%z" if (":" in re_result.group(7)) else ("%Z"))
				var_return = timegm(time.strptime("{0:d}, {1} {2} {3} {4}:{5}:{6} {7}".format(wday, re_result.group(2), mon, re_result.group(4), re_result.group(5), re_result.group(6), re_result.group(7), re_result.group(8)), "%w, %d %m %y %H:%M:%S " + timezone_format))
			#
		#

		if (var_return == None): # ANSI C
		#
			try: var_return = timegm(time.strptime(datetime))
			except: pass
		#

		if (var_return == None): raise ValueError("Given date and time is not RFC 2616 compliant formatted", 38)
		return var_return
	#
#

##j## EOF
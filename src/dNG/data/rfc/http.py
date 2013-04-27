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

from base64 import b64encode
import re

try:
#
	import http.client as http_client
	from urllib.parse import quote, urlsplit
#
except ImportError:
#
	import httplib as http_client
	from urllib import quote
	from urlparse import urlsplit
#

from .basics import direct_basics

try: _typed_object = { "bytes": unicode.encode, "bytes_type": str, "str": unicode.encode, "unicode": str.decode, "unicode_type": unicode }
except: _typed_object = { "bytes": str.encode, "bytes_type": bytes, "str": bytes.decode, "unicode": bytes.decode, "unicode_type": str }

class direct_http(direct_basics):
#
	"""
HTTP support is provided for requesting and parsing data.

:author:    direct Netware Group
:copyright: (C) direct Netware Group - All rights reserved
:package:   rfc_basics.py
:since:     v0.1.00
:license:   http://www.direct-netware.de/redirect.php?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	RE_HEADER_FIELD_ESCAPED = re.compile("([\\\]+)$")
	"""
RegExp to find escape characters
	"""

	def __init__(self, url, timeout = 6, event_handler = None):
	#
		"""
Constructor __init__(direct_http)

:param url: URL to be called
:param timeout: Connection timeout in seconds
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		global _typed_object

		self.auth_username = None
		"""
Request authorisation username
		"""
		self.auth_password = None
		"""
Request authorisation password
		"""
		self.connection = None
		"""
HTTP connection
		"""
		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
	happened.
		"""
		self.headers = None
		"""
Request headers
		"""
		self.host = None
		"""
Request host
		"""
		self.length = -1
		"""
Request body length
		"""
		self.path = None
		"""
Request path
		"""
		self.port = None
		"""
Request port
		"""
		self.timeout = timeout
		"""
Connection timeout in seconds
		"""

		if (str != _typed_object['unicode_type'] and type(url) == _typed_object['unicode_type']): url = _typed_object['str'](url, "utf-8")
		self.configure(url)
	#

	def build_request_parameters(self, params = None, separator = ";"):
	#
		"""
Build a HTTP query string based on the given parameters and the separator.

:param params: Query parameters as dict
:param separator: Query parameter separator

:access: protected
:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		var_return = None

		if (type(params) == dict):
		#
			params_list = [ ]

			for key in params:
			#
				if (type(params[key]) != bool): params_list.append("{0}={1}".format(quote(str(key)), quote(str(params[key]))))
				elif (params[key]): params_list.append("{0}=1".format(quote(str(key))))
				else: params_list.append("{0}=0".format(quote(str(key))))
			#

			var_return = separator.join(params_list)
		#

		return var_return
	#

	def configure(self, url):
	#
		"""
Returns a connection to the HTTP server.

:param url: URL to be called

:access: protected
:since:  v0.1.00
		"""

		url_elements = urlsplit(url)
		if (url_elements.username != None): self.auth_username = url_elements.username
		if (url_elements.password != None): self.auth_password = url_elements.password

		if (url_elements.hostname != None): self.host = url_elements.hostname
		self.port = (http_client.HTTP_PORT if (url_elements.port == None) else url_elements.port)
		self.path = url_elements.path
	#

	def get_connection(self):
	#
		"""
Returns a connection to the HTTP server.

:access: protected
:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		if (self.connection == None):
		#
			try: self.connection = http_client.HTTPConnection(self.host, self.port, timeout = self.timeout)
			except TypeError: self.connection = http_client.HTTPConnection(self.host, self.port)
		#

		return self.connection
	#

	def request(self, method, separator = ";", params = None, data = None):
	#
		"""
Call a given request method on the connected HTTP server.

:param method: HTTP method
:param separator: Query parameter separator
:param params: Parsed query parameters as str
:param data: HTTP body

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		global _typed_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -http.request({0}, separator, params, data)- (#echo(__LINE__)#)".format(method))

		try:
		#
			path = self.path

			if (type(params) == str):
			#
				if ("?" not in path): path += "?"
				elif (not path.endswith(separator)): path += separator

				path += params
			#

			kwargs = { "url": path }

			if (data != None):
			#
				if (type(data) != _typed_object['bytes_type']): data = _typed_object['bytes'](data, "utf-8")
				kwargs['body'] = data
			#

			if (self.auth_username != None):
			#
				base64_data = b64encode(_typed_object['unicode']("{0}:{1}".format(self.auth_username,self.auth_password), "utf-8"))
				if (type(base64_data) != str): base64_data = _typed_object['str'](base64_data, "utf-8")

				kwargs['headers'] = { "Authorization": "Basic {0}".format(base64_data) }
				if (self.headers != None): kwargs['headers'].update(self.headers)
			#
			elif (self.headers != None): kwargs['headers'] = self.headers

			connection = self.get_connection()
			connection.request(method, **kwargs)
			response = connection.getresponse()

			var_return = { "headers": { } }
			for header in response.getheaders(): var_return['headers'][header[0].lower().replace("-", "_")] = header[1]

			if (response.status == http_client.CREATED or response.status == http_client.OK or response.status == http_client.PARTIAL_CONTENT): var_return['body'] = response.read()
			else: var_return['body'] = http_client.HTTPException("{0} {1}".format(str(response.status), str(response.reason)), response.status)
		#
		except Exception as handled_exception: var_return = { "headers": None, "body": handled_exception }

		return var_return
	#

	def request_get(self, params = None, separator = ";"):
	#
		"""
Do a GET request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		params = self.build_request_parameters(params, separator)
		return self.request("GET", separator, params)
	#

	def request_head(self, params = None, separator = ";"):
	#
		"""
Do a HEAD request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		params = self.build_request_parameters(params, separator)
		return self.request("HEAD", separator, params)
	#

	def request_post(self, data = None, params = None, separator = ";"):
	#
		"""
Do a POST request on the connected HTTP server.

:param data: HTTP body
:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.00
		"""

		params = self.build_request_parameters(params, separator)
		return self.request("POST", separator, params, data)
	#

	def set_header(self, name, value, value_append = False):
	#
		"""
Sets a header.

:param name: Header name
:param value: Header value as string or array
:param value_append: True if headers should be appended

:since: v0.1.00
		"""

		if (self.headers == None): self.headers = { }

		if (value == None):
		#
			if (name in self.headers): del(self.headers[name])
		#
		elif (name not in self.headers): self.headers[name] = value
		elif (value_append):
		#
			if (type(self.headers[name]) == list): self.headers[name].append(value)
			else: self.headers[name] = [ self.headers[name], value ]
		#
	#

	def set_event_handler(self, event_handler = None):
	#
		"""
Sets the EventHandler.

:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		self.event_handler = event_handler
	#

	@staticmethod
	def header_get(data):
	#
		"""
Returns a RFC 2616 compliant dict of headers from the entire message.

:param data: Input message

:return: (str) Dict with parsed headers; False on error
:since:  v0.1.00
		"""

		header = data.split("\r\n\r\n", 1)[0]
		var_return = direct_basics.get_headers(header)

		if (var_return != False and "@nameless" in var_return and "\n" not in var_return['@nameless']):
		#
			var_return['@http'] = var_return['@nameless']
			del(var_return['@nameless'])
		#

		return var_return
	#

	@staticmethod
	def header_field_list(message):
	#
		"""
Returns a RFC 2616 compliant list of fields from a header message.

:param field: Header message

:return: (str) List containing str or dict if a field name was identified;
         False on error
:since:  v0.1.00
		"""

		var_return = [ ]

		fields = [ ]
		last_position = 0
		message_length = (len(message) if (type(message) == str) else 0)

		while (last_position > -1 and last_position < message_length):
		#
			comma_position = message.find(",", last_position)
			quotation_mark_position = message.find('"', last_position)
			next_position = -1

			if (comma_position > -1): next_position = comma_position

			if (quotation_mark_position > -1 and (next_position < 0 or next_position > quotation_mark_position)):
			#
				next_position = direct_http.header_field_list_find_end_position(message[last_position:], quotation_mark_position - last_position, '"')
				if (next_position > -1): next_position += last_position
			#

			if (next_position < 0):
			#
				fields.append(message[last_position:])
				last_position = -1
			#
			else:
			#
				fields.append(message[last_position:next_position])
				if (message[next_position:1 + next_position] == ","): next_position += 1
				last_position = next_position
			#
		#

		for field in fields:
		#
			if (":" in field):
			#
				field = field.split(":", 1)
				field = { field[0].strip(): field[1].strip() }
			#
			else: field.strip()

			var_return.append(field)
		#

		return var_return
	#

	@staticmethod
	def header_field_list_find_end_position(data, position, end_char):
	#
		"""
Returns a RFC 2616 compliant list of fields from a header message.

:param field: Header message

:access: protected
:return: (str) List containing str or dict if a field name was identified;
         False on error
:since:  v0.1.00
		"""

		next_position = position
		var_return = -1

		while (end_char != None):
		#
			next_position = data.find(end_char, 1 + next_position)
			re_result = (None if (next_position < 1) else direct_http.RE_HEADER_FIELD_ESCAPED.search(data[position:next_position]))

			if (next_position < 1): end_char = None
			elif (re_result == None or (len(re_result.group(1)) % 2) == 0):
			#
				var_return = 1 + next_position
				end_char = None
			#
		#

		return var_return
	#
#
#

##j## EOF
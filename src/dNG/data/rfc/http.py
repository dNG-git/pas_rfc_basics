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
	from urllib.parse import quote as url_quote
#
except ImportError:
#
	import httplib as http_client
	from urllib import quote as url_quote
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
		if (event_handler != None): event_handler.debug("#echo(__FILEPATH__)# -http.__init__()- (#echo(__LINE__)#)")

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
		self.port = None
		"""
Request port
		"""
		self.uri = None
		"""
Request URI
		"""

		if (str != _typed_object['unicode_type'] and type(url) == _typed_object['unicode_type']): url = _typed_object['str'](url, "utf-8")
		re_result = re.match("^http://(.+?)@(.+?):(\\d+)(.*?)$", url)

		if (re_result == None): re_result = re.match("^http://(.+?):(\\d+)(.*?)$", url)
		else:
		#
			auth_data = re_result.group(1).split(":", 1)
			re_result = re.match("^http://(.+?):(\\d+)(.*?)$", "http://{0}:{1}{2}".format(re_result.group(2), re_result.group(3), re_result.group(4)))

			if (len (auth_data) > 1): self.auth_password = auth_data[1]
			else: self.auth_password = ""

			self.auth_username = auth_data[0]
		#

		if (re_result == None):
		#
			re_result = re.match("^http://(.+?)/(.*?)$", url)
			self.port = http_client.HTTP_PORT

			if (re_result != None):
			#
				self.host = re_result.group(1)
				self.uri = "/{0}".format(re_result.group(2))
			#
		#
		else:
		#
			self.host = re_result.group(1)
			self.port = int(re_result.group(2))
			self.uri = re_result.group(3)
		#

		try: self.connection = http_client.HTTPConnection(self.host, self.port, timeout = timeout)
		except TypeError: self.connection = http_client.HTTPConnection(self.host, self.port)
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
			url = self.uri

			if (type(params) == str):
			#
				if ("?" not in url): url += "?"
				elif (not url.endswith(separator)): url += separator

				url += params
			#

			kwargs = { "url": self.uri }

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

			self.connection.request(method, **kwargs)
			response = self.connection.getresponse()

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

		if (type(params) == dict):
		#
			params_list = [ ]

			for key in params:
			#
				if (type(params[key]) != bool): params_list.append("{0}={1}".format(url_quote(str(key)), url_quote(str(params[key]))))
				elif (params[key]): params_list.append("{0}=1".format(url_quote(str(key))))
				else: params_list.append("{0}=0".format(url_quote(str(key))))
			#

			params = separator.join(params_list)
		#

		return self.request("GET", separator, params)
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

		if (type(params) == dict):
		#
			params_list = [ ]

			for key in params:
			#
				if (type(params[key]) != bool): params_list.append("{0}={1}".format(url_quote(str(key)), url_quote(str(params[key]))))
				elif (params[key]): params_list.append("{0}=1".format(url_quote(str(key))))
				else: params_list.append("{0}=0".format(url_quote(str(key))))
			#

			params = separator.join(params_list)
		#

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

		if (event_handler != None): event_handler.debug("#echo(__FILEPATH__)# -http.set_event_handler(event_handler)- (#echo(__LINE__)#)")
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
#

##j## EOF
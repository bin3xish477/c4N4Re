"""
MIT License

Copyright (c) 2021 Alexis Rodriguez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from logging import getLogger

from os import environ

from sys import exit

from base64 import b64encode

class Login:
	def __init__(self, config):
		self.config    = config
		self.logger    = getLogger(__name__)
		self._email    = ""
		self._app_pass  = ""

	@property
	def email(self):
		return self._email

	@property
	def app_pass(self):
		return self._app_pass
	
	def env_login(self):
		try:
			self._email    = environ["EMAIL_ADDR"]
			self._app_pass = environ["EMAIL_PASS"]
		except KeyError as e:
			self.logger.critical("EMAIL_ADDR or EMAIL_PASS environment variables not set")
			exit(1)

		if not self.config.has_section("login"):
			self.logger.info("adding `login` section to config file")
			self.config.add_section("login")
			self.config.set("login", "email", b64encode(bytes(self.email, "utf8")).decode("utf8"))
			self.config.set("login", "app_pass", b64encode(bytes(self.app_pass, "utf8")).decode("utf8"))
		else:
			if self.config["login"]["email"] != self.email:
				self.logger.info("updating login email")
				self.config["login"]["email"] = b64encode(bytes(self.email, "utf8")).decode("utf8")
			if self.config["login"]["app_pass"] != self.app_pass:
				self.logger.info("updating login app password")
				self.config["login"]["app_pass"] = b64encode(bytes(self.app_pass, "utf8")).decode("utf8")

		with open("config.ini", "w") as f:
			self.config.write(f)

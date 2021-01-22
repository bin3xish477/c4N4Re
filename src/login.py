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

from tkinter import Tk
from tkinter import Label
from tkinter import Button
from tkinter import Entry
from tkinter import messagebox

from passlib.context import CryptContext

from logging import getLogger

from os import environ

class Login:
	def __init__(self, config):
		self.config    = config
		self.context   = CryptContext(
					schemes=["pbkdf2_sha256"],
					default="pbkdf2_sha256",
					pbkdf2_sha256__default_rounds=30000)
		self.logger    = getLogger(__name__)
		self._email    = ""
		self._password = ""

	@property
	def email(self):
		return self._email

	@email.setter
	def email(self, arg):
		self._email = arg

	@property
	def password(self):
		return self._password

	@password.setter
	def password(self, arg):
		self._password = arg
	
	@property
	def password_hash(self):
		return self._password_hash

	def env_login(self):
		try:
			self._email    = environ["EMAIL_ADDR"]
			self._password = environ["EMAIL_PASS"]
		except KeyError as e:
			self.logger.critical("EMAIL_ADDR or EMAIL_PASS environment variables not set")
			self.prompt()
			return

		if not self.config.has_section("login"):
			self.config.add_section("login")
			self.config["login"]["email"] = self.email
			self.config["login"]["password_hash"] = self.context.encrypt(self.password) 
		else:
			if self.config["login"]["email"] != self.email:
				self.config["login"]["email"] = self.email
				self.config["login"]["password_hash"] = self.context.encrypt(self.password) 
			else:
				if not self.context.verify(self.password, self.config["login"]["password_hash"]):
					log.critical(f"Invalid password for email: {self.email}")
					exit(1)

		with open("config.ini", "w") as f:
			self.config.write(f)

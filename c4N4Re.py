#!/usr/bin/env python3

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

__author__  = "BinexisHATT"
__date__    = "01/21/2021"
__version__ = 1.0

from configparser import ConfigParser

from src.watcher import Watcher
from src.login import Login

from sys import exit

from logging import getLogger, INFO, basicConfig

logger = getLogger(__name__)
format_ = "[%(asctime)s]:%(filename)s:%(lineno)s:%(message)s"
basicConfig(
    format=format_, level=INFO,
    filename="c4N4Re.log", filemode='w'
)

if __name__ == "__main__":
	config = ConfigParser()
	config.read("config.ini")

	if (not config.has_section("login")
		or not config.has_option("login", "email")
		or not config.has_option("login", "app_pass")):
		login = Login(config=config)
		try:
			login.env_login()
		except:
			logger.critical("Unable to retrieve email or app password values from config file.")

	try:
		watcher = Watcher(config=config)
		watcher.watch()
	except KeyboardInterrupt:
		logger.info("Captured KeyboardInterrupt exception. Exiting program")
		exit(1)
	except Exception as e:
		logger.critical(f"Exception -> {e}")
		exit(1)

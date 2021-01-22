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
__date__    = 1_21_2021
__version__ = 1.0

from configparser import ConfigParser

from src.watcher import Watcher
from src.login import Login

from sys import exit

from logging import getLogger, INFO, basicConfig

logger = getLogger(__name__)
format_ = "[%(asctime)s] : %(filename)s : %(message)s"
basicConfig(
    format=format_, level=INFO,
    filename="c4N4Re.log", filemode='w'
)

if __name__ == "__main__":
	config = ConfigParser()
	config.read("config.ini")

	l = Login(config=config)
	if not config.getboolean("general", "ignore_password_prompt"):
		l.prompt()
	elif config.getboolean("general", "use_env_vars_for_login"):
		l.env_login()
	else:
		try:
			l.email    = config["login"]["email"]
			l.password = config["login"]["password"]
		except:
			logger.critical(
				"Unable to retrieve email or password values from config file. Prompting user for creds"
				)
			l.prompt()

	try:
		watcher = Watcher(config, l.password)
		watcher.watch()
	except AttributeError as e:
		print(e)
		logger.critical("Password has not been set. Prompting user for creds")
		l.prompt()
	except KeyboardInterrupt:
		logger.info("Captured KeyboardInterrupt exception. Exiting program")
		exit(1)
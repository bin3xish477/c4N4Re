#!/usr/bin/env python3

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
	elif config.getboolean("general", "use_env_login_arguments"):
		l.env_login()

	try:
		watcher = Watcher(config, l.password)
		watcher.watch()
	except AttributeError:
		logger.critical("Password has not been set")
		exit(1)

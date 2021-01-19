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
    filename="c4N4Re.log", filemode='a'
)

if __name__ == "__main__":
	config = ConfigParser()
	config.read("config.ini")

	if not config.getboolean("general", "ignore_password_prompt"):
		l = Login(config=config)
		l.prompt()
	elif config.getboolean("general", "use_env_login_arguments"):
		l = Login()
		l.env_login()

	try:
		watcher = Watcher(config, l.password)
		watcher.watch()
	except AttributeError:
		logger.critical("Password has not been set")
		exit(1)

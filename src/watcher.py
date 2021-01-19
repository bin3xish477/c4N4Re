from src.emailer import Emailer

from psutil import cpu_percent
from psutil import virtual_memory
from psutil import net_connections
from psutil import process_iter
from psutil import NoSuchProcess
from psutil import AccessDenied
from psutil import ZombieProcess

from os import stat

from os.path import exists, realpath

from time import sleep

from sys import exit

from logging import getLogger

class Watcher:
    def __init__(self, config, password):
        self.config   = config
        self.password = password
        self.num_of_alerts = 0
        self.logger = getLogger(__name__)

    def _cpu(self):
        pass
    
    def _ram(self):
        pass
    
    def _disk(self):
        pass

    def _ssh(self):
        pass

    def _files(self):
        pass

    def _services(self):
        monitored_services = list(
            map(lambda s: s.lower(), self.config["services"]["monitor"].split("|"))
            )
        for process in process_iter():
            try:
                if process.name().lower() in monitored_services:
                    message = f"c4N4Re has detected a running service " \
                    f"currently being monitored: {process.name()}"
                    self.send_alert(
                        self.config["services"]["subject"],
                        message)
            except (NoSuchProcess, AccessDenied, ZombieProcess):
                self.logger.info("An Attempt to get a processes name failed")
                continue

    def _startup(self):
        """
        Allow user in config.ini to specify what exectuables should be present
        in the startup registry entry. If a new entry appears, send email.
        """
        pass

    def watch(self):
        while True:
            self._services()
            sleep(int(self.config["general"]["interval_between_evaluations"]))

    def send_alert(self, subject, message):
        if self.num_of_alerts == self.config["general"]["max_alerts"]:
            exit(1)

        server = self.config["smtp"]["server"]
        port   = self.config["smtp"]["port"]

        with Emailer(server, port) as email:
            login = self.config["login"]
            try:
                email.authenticate(login["email"], self.password)
                email.send(login["email"], subject, message)
            except:
                self.logger.critical("An error occured with the SMTP")
                exit(1)

        if self.config.getboolean("general", "continue_beyond_initial_alert"):
            return
        else:
            exit(0)

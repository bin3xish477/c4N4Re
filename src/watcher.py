from src.emailer import Emailer

from psutil import cpu_percent
from psutil import virtual_memory
from psutil import net_connections
from psutil import process_iter
from psutil import disk_usage
from psutil import NoSuchProcess
from psutil import AccessDenied
from psutil import ZombieProcess

from netaddr import IPNetwork

from os import stat

from os.path import exists, realpath

from time import sleep

from sys import exit

from logging import getLogger

class Watcher:
    def __init__(self, config, password):
        self.config                        = config
        self.password                      = password
        self.num_of_alerts                 = 0
        self.logger                        = getLogger(__name__)
        self.max_alerts                    = self.config["general"]["max_alerts"]
        self.continue_beyond_initial_alert = self.config.getboolean("general", "continue_beyond_initial_alert")

        if self.config.has_option("ip", "subnet_blocklist"):
            self.ip_blocklist = list(ip for s in self.config["ip"]["subnet_blocklist"].split("|") for ip in IPNetwork(s.strip()))

    def _cpu(self):
        pass
    
    def _ram(self):
        pass
    
    def _disks(self):
        for drive in self.config["disks"]["drives"].split("|"):

            drive                  = drive.strip()
            drive_usage_percentage = disk_usage(drive).percent
            max_disk_util          = float(self.config["disks"]["max_disk_util"])

            if drive_usage_percentage > max_disk_util:
                message = f"c4N4Re has detected a storage drive ({drive}) that has " \
                          f"exceeded the max disk utilization percentage of {max_disk_util}%."
                self.send_alert(
                    self.config["disks"]["subject"],
                    message
                    )
                self.num_of_alerts += 1

    def _ssh(self):
        max_concurrent_ssh_connections = int(self.config["ssh"]["max_concurrent_ssh_connections"])

        ssh_conns = 0
        for conn in net_connections():
            if conn.laddr.port == 22 or (conn.raddr and conn.raddr.port == 22):
                ssh_conns += 1
            if ssh_conns > max_concurrent_ssh_connections:
                message = f"c4N4Re has detected that there are concurrent SSH connections" \
                          f" and has exceeded the max SSH connections allowed: {max_concurrent_ssh_connections}"
                self.send_alert(
                    self.config["ssh"]["subject"],
                    message)
                break

    def _ip(self):
        for conn in net_connections():
            if conn.laddr.ip in self.ip_blocklist:
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
                    self.num_of_alerts += 1
            except (NoSuchProcess, AccessDenied, ZombieProcess):
                self.logger.info("An attempt to get a processes name failed")
                continue

    def _startup(self):
        """
        Allow user in config.ini to specify what exectuables should be present
        in the startup registry entry. If a new entry appears, send email.
        """
        pass

    def watch(self):
        while True:
            if self.config.has_section("services"):
                self._services()

            if self.config.has_section("disks"):
                self._disks()

            if self.config.has_section("ssh"):
                self._ssh()

            sleep(int(self.config["general"]["interval_between_evaluations"]))

    def send_alert(self, subject, message):
        if self.num_of_alerts == self.max_alerts:
            exit(1)

        server = self.config["smtp"]["server"]
        port   = self.config["smtp"]["port"]

        with Emailer(server, port) as email:
            login = self.config["login"]
            try:
                email.authenticate(login["email"], self.password)
                email.send(login["email"], subject, message)
            except:
                self.logger.critical("An error occured with SMTP")
                exit(1)

        if self.continue_beyond_initial_alert:
            return
        else:
            exit(0)

from src.emailer import Emailer

from psutil import cpu_percent
from psutil import cpu_count
from psutil import cpu_freq
from psutil import virtual_memory
from psutil import net_connections
from psutil import process_iter
from psutil import disk_usage
from psutil import NoSuchProcess
from psutil import AccessDenied
from psutil import ZombieProcess

from winreg import ConnectRegistry
from winreg import OpenKey
from winreg import HKEY_LOCAL_MACHINE
from winreg import EnumKey
from winreg import EnumValue
from winreg import QueryInfoKey
from winreg import QueryValueEx
from winreg import KEY_ALL_ACCESS

from netaddr import IPNetwork

from os import stat

from os.path import exists, realpath

from time import sleep

from sys import exit

from logging import getLogger

from platform import system

from re import search

class Watcher:
    def __init__(self, config, password):
        self.config                        = config
        self.password                      = password
        self.num_of_alerts                 = 0
        self.logger                        = getLogger(__name__)
        self.system                        = system()
        self.max_alerts                    = int(self.config["general"]["max_alerts"])
        self.continue_beyond_initial_alert = self.config.getboolean("general", "continue_beyond_initial_alert")

        if self.config.has_option("ip", "subnet_blocklist"):
            self.ip_blocklist = list(ip for s in self.config["ip"]["subnet_blocklist"].split("|") for ip in IPNetwork(s.strip()))

    def _cpu(self):
        max_cpu_util = float(self.config["cpu"]["max_util"])

        if cpu_percent() > max_cpu_util:
            _cpu_freq    = cpu_freq()
            current_freq = _cpu_freq.current
            min_freq     = _cpu_freq.min
            max_freq     = _cpu_freq.max
            _cpu_count   = cpu_count()

            message = f"c4N4Re has detected that CPU utilization has exceeded the maximum " \
                      f"utilization percentage currently set to {max_cpu_util}%\n" \
                      f"CPU Stats:\n\tCount = {_cpu_count}\n\tCurrent Frequency = {current_freq}" \
                      f"\n\tMinimun Frequency = {min_freq}\n\tMaximum Frequency = {max_freq}\n"
            self._send_alert(
                self.config["cpu"]["subject"],
                message)
            self.num_of_alerts += 1
    
    def _ram(self):
        _virtual_memory = virtual_memory()
        max_ram_util = float(self.config["ram"]["max_util"])

        if _virtual_memory.percent > max_ram_util:
            gb = 2 ** 30
            ram_total     = _virtual_memory.total / gb
            ram_available = _virtual_memory.available / gb
            ram_used      = _virtual_memory.used / gb
            ram_free      = _virtual_memory.free / gb

            message = f"c4N4Re has detected that RAM utilization has exceeded the maximum " \
                      f"utilization percentage currently set to {max_ram_util}%." \
                      f"\nRAM Stats:\n\tTotal = {ram_total}\n\tAvailable = {ram_available}" \
                      f"\n\tUsed = {ram_used}\t\nFree = {ram_free}\n"
            self._send_alert(
                self.config["ram"]["subject"],
                message)
            self.num_of_alerts += 1
    
    def _disks(self):
        max_disk_util = float(self.config["disks"]["max_util"])

        for drive in self.config["disks"]["drives"].split("|"):
            drive            = drive.strip()
            drive_stats   = disk_usage(drive)
            drive_percentage = drive_stats.percent

            if drive_percentage > max_disk_util:
                gb = 2 ** 30
                drive_space   = drive_stats.total / gb
                drive_used    = drive_stats.used / gb
                drive_free    = drive_stats.free / gb
                max_disk_util = float(self.config["disks"]["max_util"])

                message = f"c4N4Re has detected a storage drive ({drive}) that has " \
                          f"exceeded the max disk utilization percentage of {max_disk_util}%." \
                          f"\n{drive} Stats:\n\tTotal Space = {drive_space}\n\tUsed Space = {drive_used}" \
                          f"\n\tFree Space = {drive_free}\n\tUsed Space in Percentage = {drive_percentage}%"
                self._send_alert(
                    self.config["disks"]["subject"],
                    message)
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
                self._send_alert(
                    self.config["ssh"]["subject"],
                    message)
                self.num_of_alerts += 1
                break

    def _ip(self):
        for conn in net_connections():
            if conn.laddr.ip in self.ip_blocklist:
                pass

    def _files(self):
        self.num_of_alerts += 1

    def _services(self):
        monitored_services = list(
            map(lambda s: s.lower(), self.config["services"]["monitor"].split("|"))
            )
        for process in process_iter():
            try:
                if process.name().lower() in monitored_services:
                    message = f"c4N4Re has detected a running service " \
                    f"currently being monitored: {process.name()}"
                    self._send_alert(
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
        self.num_of_alerts += 1

    def _users(self):
        r"""
        (Windows)
            This function checks the registry key:
            ``SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList``
            for user sids. If a new account is created, the alert will be triggered
            after the system is rebooted and is updated to reflect the creation of the account.

        (Linux)
            Open the etc/passwd file and extracts all the user's. If a new user is found within
            this file or if a service account shell has been updated to an interactive logon shell,
            an alert will be triggered
        """
        target_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
        allowed_users = list(map(lambda s: s.strip(), self.config["users"]["allow_list"].split("|")))

        if self.system == "Windows":
            with ConnectRegistry(None, HKEY_LOCAL_MACHINE) as hklm:
                with OpenKey(hklm, target_key, 0, KEY_ALL_ACCESS) as profile_list:

                    subkeys = QueryInfoKey(profile_list)[0]
                    for i in range(subkeys):
                        subkey = EnumKey(profile_list, i)
                        if search(r"^S-\d-\d+-(\d+-){1,14}\d+$", subkey):

                            with OpenKey(hklm, f"{target_key}\\{subkey}", 0, KEY_ALL_ACCESS) as user_key:

                                user = QueryValueEx(user_key, r"ProfileImagePath")[0].split("\\")[-1]

                                if user not in allowed_users:
                                    message = f"c4N4Re has detected a new user: {user}. " \
                                              f"If you did not create this new user, your system might be compromised!"
                                    self._send_alert(
                                        self.config["users"]["subject"],
                                        message)
                                    self.num_of_alerts += 1
        else:
            with open("/etc/passwd") as passwd:
                pass
            #self._send_alert()
            #self.num_of_alerts += 1

    def _groups(self):
        self.num_of_alerts += 1
    
    def _send_alert(self, subject, message):
        if self.num_of_alerts == self.max_alerts:
            exit(1)

        server = self.config["smtp_config"]["server"]
        port   = self.config["smtp_config"]["port"]

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

    def watch(self):
        while True:
            if self.config.has_section("cpu"):
                self._cpu()
            if self.config.has_section("ram"):
                self._ram()
            if self.config.has_section("disks"):
                self._disks()
            if self.config.has_section("services"):
                self._services()
            if self.config.has_section("disks"):
                self._disks()
            if self.config.has_section("ssh"):
                self._ssh()
            if self.config.has_section("users"):
                self._users()

            sleep(int(self.config["general"]["interval_between_evaluations"]))
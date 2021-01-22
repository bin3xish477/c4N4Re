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

from src.emailer import Emailer

from platform import system

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

if system() == "Windows":
    from winreg import ConnectRegistry
    from winreg import OpenKey
    from winreg import HKEY_LOCAL_MACHINE
    from winreg import EnumKey
    from winreg import EnumValue
    from winreg import QueryInfoKey
    from winreg import QueryValueEx
    from winreg import KEY_ALL_ACCESS
    
    from win32net import NetLocalGroupEnum

from netaddr import IPNetwork

from os import stat

from os.path import exists, realpath

from time import sleep

from sys import exit

from logging import getLogger

from re import search

from base64 import b64decode

class Watcher:
    def __init__(self, config):
        self.config                        = config
        self.num_of_alerts                 = 0
        self.logger                        = getLogger(__name__)
        self.system                        = system()
        self.max_alerts                    = int(self.config["general"]["max_alerts"])
        self.continue_beyond_initial_alert = self.config.getboolean("general", "continue_beyond_initial_alert")

        if self.config.has_option("ip", "subnet_blocklist"):
            valid_subnets = []
            for subnet in list(map(lambda s: s.strip(), self.config["ip"]["subnet_blocklist"].split("|"))):
                if search(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", subnet) or search(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}/\d{1,2}", subnet):
                    valid_subnets.append(subnet)
                else:
                    self.logger.info("An invalid subnet was detected in the config file")
                    continue
            self.ip_blocklist = [IPNetwork(s.strip()) for s in valid_subnets]

        if self.system == "Windows":
            if self.config.has_section("local_groups") and self.config["local_groups"]["allow_list"].strip() == "":
                self.groups = [group["name"] for group in NetLocalGroupEnum(None, 0, 0)[0]]
                self.config.set("local_groups", "allow_list", "|".join(self.groups))
                with open("config.ini", "w") as f:
                    self.config.write(f)
        else:
            if self.config.has_section("local_groups") and self.config["local_groups"]["allow_list"].strip() == "":
                self.groups = []
                with open("/etc/group") as f:
                    for line in f:
                        self.groups.append(line.split(':')[0])
                    self.config.set("local_groups", "allow_list", "|".join(self.groups))
                    with open("config.ini", "w") as c:
                        self.config.write(c)

        if self.config.has_section("files"):
            self.monitored_files = list(
                map(lambda s: s.lower(), self.config["files"]["monitor"].split("|"))
            )
            self.monitored_files_access_times = {}
            for _file in self.monitored_files:
                if exists(_file):
                    self.monitored_files_access_times[_file] = stat(_file).st_atime
                else:
                    self.logger.info("{_file} does not exists")

    def _cpu(self):
        if self.config.has_option("cpu", "max_util") and self.config["cpu"]["max_util"] != "":
            max_cpu_util = float(self.config["cpu"]["max_util"])
        else:
            self.logger.warning("The CPU canary will not run because a maximun CPU " \
                "utilization value, `max_util`, was not found in the config file")
            self.cpu_canary = False
            return

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
        if self.config.has_option("ram", "max_util") and self.config["ram"]["max_util"] != "":
            max_ram_util = float(self.config["ram"]["max_util"])
        else:
            self.logger.warning("The RAM canary will not run because a maximun RAM " \
                "utilization value, `max_util`, was not found in the config file")
            self.ram_canary = False
            return

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
        if self.config.has_option("disks", "max_util") and self.config["disks"]["max_util"] != "":
            max_disk_util = float(self.config["disks"]["max_util"])
        else:
            self.logger.warning("The disk canary will not run because a maximun disk " \
                "utilization value, `max_util`, was not found in the config file")
            self.disk_canary = False
            return

        try:
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
        except FileNotFoundError:
            self.logger.warning("The disk canary will not run because no drives were specified in config file")
            self.disks_canary = False

    def _ssh(self):
        if self.config.has_option("ssh", "max_ssh_connections") and self.config["ssh"]["max_ssh_connections"] != "":
            max_ssh_connections = int(self.config["ssh"]["max_ssh_connections"])
        else:
            self.logger("The SSH canary will not run because no value for `max_ssh_connections` was specified" \
                " the config file")
            self.ssh_canary = False

        ssh_conns = 0
        for conn in net_connections():
            if conn.laddr.port == 22 or (conn.raddr and conn.raddr.port == 22):
                ssh_conns += 1
            if ssh_conns > max_ssh_connections:
                message = f"c4N4Re has detected that there are concurrent SSH connections" \
                          f" and has exceeded the max SSH connections allowed: {max_ssh_connections}"
                self._send_alert(
                    self.config["ssh"]["subject"],
                    message)
                self.num_of_alerts += 1
                break

    def _ip(self):
        detected_blacklisted_ip = False
        if self.ip_blocklist:
            for conn in net_connections():
                local_ip = conn.laddr.ip
                if conn.raddr:
                    remote_ip = conn.raddr.ip
                else:
                    remote_ip = False
                for network in self.ip_blocklist:
                    if local_ip in network:
                        message = f"c4N4Re has detected the presence of an IP address in a blocklisted subnet: {local_ip}."
                        detected_blacklisted_ip = True
                    elif remote_ip and remote_ip in network:
                        message = f"c4N4Re has detected the presence of an IP address in a blocklisted subnet: {remote_ip}."
                        detected_blacklisted_ip = True
                    if detected_blacklisted_ip:
                        self._send_alert(
                            self.config["ip"]["subject"],
                            message)
                        self.num_of_alerts += 1

        else:
            self.logger.info("The IP blocklist canary will not run because no IP or subnet was found in config file")
            self.ip_canary = False

    def _files(self):
        if len(self.monitored_files_access_times) != 0 and len(self.monitored_files) != 0:
            for _file in self.monitored_files:
                if stat(_file).st_atime != self.monitored_files_access_times[_file]:
                    message = f"c4N4Re has detected that some accessed the file {_file}."
                    self._send_alert(
                        self.config["files"]["subject"],
                        message)
                    self.num_of_alerts += 1
                    break

    def _processes(self):
        monitored_services = list(
            map(lambda s: s.lower(), self.config["processes"]["monitor"].split("|"))
            )
        for process in process_iter():
            try:
                if process.name().lower() in monitored_services:
                    message = f"c4N4Re has detected a running service " \
                    f"currently being monitored: {process.name()}"
                    self._send_alert(
                        self.config["processes"]["subject"],
                        message)
                    self.num_of_alerts += 1
            except (NoSuchProcess, AccessDenied, ZombieProcess):
                self.logger.info("An attempt to get a processes name failed")
                continue

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
                                    message = f"c4N4Re has detected a interactive new user: {user}. " \
                                              f"If you have not created a new user or have not changed the shell " \
                                              f"for a service account, then your system might be compromised!"
                                    self._send_alert(
                                        self.config["users"]["subject"],
                                        message)
                                    self.num_of_alerts += 1
        else:
            linux_shells = (
                            "bash", # GNU Bourne-Again Shell
                            "sh",   # Bourne Shell
                            "ksh",  # Korn Shell
                            "zsh",  # Z Shell
                            "csh"   # C Shell
                            ) 
            interactive_users = []
            allowed_users = list(map(lambda s: s.strip(), self.config["users"]["allow_list"].split('|')))

            with open("/etc/passwd") as passwd:
                for entry in passwd:
                    entry = entry.strip().split(":")
                    user, shell = entry[0], entry[-1].split('/')[-1]
                    if shell in linux_shells:
                        interactive_users.append(user)
                    for interactive_user in interactive_users:
                        if interactive_user not in allowed_users:
                            message = f"c4N4Re has detected a new interactive user: {interactive_user}. " \
                                      f"If you have not created a new user or have not changed the shell " \
                                      f"for a service account, then your system might be compromised!"
                            self._send_alert(
                                self.config["users"]["subject"],
                                message)
                            self.num_of_alerts += 1

    def _local_groups(self):
        if "groups" not in self.__dict__:
            allowed_groups = list(map(lambda s: s.strip(), self.config["local_groups"]["allow_list"].split("|")))
        else:
            allowed_groups = self.groups

        if self.system == "Windows":
            for group in NetLocalGroupEnum(None, 0, 0)[0]:
                group = group["name"]
                if group not in allowed_groups:
                    message = f"c4N4Re has detected the creation of a new local group: {group}. " \
                              f"This group may have been created after installing a new application " \
                              f"but this may have also been created by an adversary. Further research " \
                              f"is encouraged."
                    self._send_alert(
                        self.config["local_groups"]["subject"],
                        message)
                    self.num_of_alerts += 1
        else:
            with open("/etc/group") as group:
                for grp in group:
                    grp = grp.split(":")[0]
                    if grp not in allowed_groups:
                        message = f"c4N4Re has detected the creation of a new group: {grp}. " \
                                  f"This group may have been created after installing a new application " \
                                  f"but this may have also been created by an adversary. Further research " \
                                  f"is encouraged."
                        self._send_alert(
                            self.config["local_groups"]["subject"],
                            message)
                        self.num_of_alerts += 1
    
    def _send_alert(self, subject, message):
        """Sends an alert to an email account"""
        if self.num_of_alerts == self.max_alerts:
            exit(0)

        server = self.config["smtp_config"]["server"]
        port   = self.config["smtp_config"]["port"]

        with Emailer(server, port) as emailer:
            login = self.config["login"]
            email = b64decode(login["email"]).decode("utf8")
            app_pass = b64decode(login["app_pass"]).decode("utf8")
            try:
                emailer.authenticate(email, app_pass)
                emailer.send(email, subject, message)
            except:
                self.logger.critical("An error sending alert email via SMTP")
                exit(1)

        if self.continue_beyond_initial_alert:
            return
        else:
            exit(0)

    def watch(self):
        if self.config.has_section("cpu"):          self.cpu_canary = True
        if self.config.has_section("ram"):          self.ram_canary = True
        if self.config.has_section("disks"):        self.disk_canary = True
        if self.config.has_section("files"):        self.files_canary = True
        if self.config.has_section("processes"):    self.processes_canary = True
        if self.config.has_section("ssh"):          self.ssh_canary = True
        if self.config.has_section("ip"):           self.ip_canary = True
        if self.config.has_section("users"):        self.users_canary = True
        if self.config.has_section("local_groups"): self.local_groups_canary = True

        interval_between_checks = int(self.config["general"]["interval_between_checks"])
        while True:
            if self.cpu_canary:          self._cpu()
            if self.ram_canary:          self._ram()
            if self.disk_canary:         self._disks()
            if self.files_canary:        self._files()
            if self.processes_canary:    self._processes()
            if self.ssh_canary:          self._ssh()
            if self.ip_canary:           self._ip()
            if self.users_canary:        self._users()
            if self.local_groups_canary: self._local_groups()

            sleep(interval_between_checks)
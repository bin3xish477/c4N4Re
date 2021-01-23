# c4N4Re

**c4N4Re** (pronounced "canary") is a Python program to easily enable a variety of system canaries.

## Setup

Installing Python Dependencies for **Windows**:

```
python3 -m pip install -U -r windows_requirements.txt
```

Installing Python Dependencies for **Linux**:

```
python3 -m pip install -U -r linux_requirements.txt
```

Configure access times in /etc/fstab:
    - https://opensource.com/article/20/6/linux-noatime
    - https://askubuntu.com/questions/985030/mount-with-atime

Example `/etc/fstab` file:

```
# /etc/fstab: static file system information.
#
# Use 'blkid' to print the universally unique identifier for a
# device; this may be used with UUID= as a more robust way to name devices
# that works even if disks are added and removed. See fstab(5).
#
# systemd generates mount units based on this file, see systemd.mount(5).
# Please run 'systemctl daemon-reload' after making changes here.
#
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
# / was on /dev/sda5 during installation
UUID=f7a7012f-74d9-49a9-a352-abaaa98ec476 /               btrfs   strictatime,nodatacow,compress,discard 0       0
# /boot was on /dev/sda1 during installation
UUID=cdc89b31-ed23-4663-a72b-8139ef673fc1 /boot           ext4    strictatime,defaults        0       2
/swapfile                                 none            swap    sw              0       0
/dev/sr0        /media/cdrom0   udf,iso9660 user,noauto     0       0
```

## STMP Authentication and Setup

**NOTE**: c4N4Re will store your email credentials in it's config file, so when deployed within a honeypot, it's best to setup another email account that is specifically used for receiving alerts from c4N4Re and nothing else. This email account should also not be linkable to your main email accounts.

c4N4Re will look for the environment variables: `EMAIL_ADDR` and `EMAIL_PASS`', where the former is the email address and the latter is the password for the specified email address. If you are using Gmail, as most people are, it is advised to [create an app password](https://www.lifewire.com/get-a-password-to-access-gmail-by-pop-imap-2-1171882). 

**Setting environment variables in Linux**

```bash
export EMAIL_ADDR='Your_email_address'
export EMAIL_PASS='Your_email_password'
```

**Setting environment variables in PowerShell**

```powershell
$Env:EMAIL_ADDR='Your_email_address'
$Env:EMAIL_PASS='Your_email_password'
```

**Adding SMTP Server and Port to Config File**

Using Gmail will require the following server and port:

```ini
[smtp_config]
server = smtp.gmail.com
port = 465
```

but of course, if you have a different SMTP server you wish to use, just set the server and port values under the `smtp_config` section in the confile file as shown above.

**NOTE**: After running c4N4Re once, you can delete the environment variables you created because they will get stored in the config.ini for c4N4Re to use again the next time it runs.

## Usage 

**Enabling Canaries**

Using c4N4Re is all about the `config.ini` file. Uncommenting any section, excluding the "general" and "smtp_config" sections, will be configured to automatically activate a canary corresponding to the name of that section. 

### CPU Canary

```ini
[cpu]
max_util = 80.0
subject = [ATTENTION] CPU Utilization Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option specifies the subject header for the alert you will recieve if this canary is triggered.

### RAM Canary

```ini
[ram]
max_util = 80.0
subject = [ATTENTION] RAM Utilization Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### Storage Disks Canary

```ini
[disks]
drives = C:\
max_util = 80.0
subject = [ATTENTION] Disk Utilization Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### SSH Canary

```ini
[ssh]
max_ssh_connections = 1
subject = [ATTENTION] Concurrnt SSH Connection Max Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### IP Canary

```ini
[ip]
subnet_blocklist = 31.33.7.0/24
subject = [ATTENTION] Blacklisted IP Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### Ports Canary

```ini
[ports]
deny = 22|80
subject = [ATTENTION] Port Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

###  FileCanary

```ini
[files]
monitor = secrets.txt|C:\Users\binexis\important.txt
subject = [Custom subject header for email]
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### Process Canary

```ini
[processes]
monitor = notepad.exe
subject = [ATTENTION] Process Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### New User Canary

```ini
[users]
allow = rodri
subject = [ATTENTION] New User Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

### New Local Group Canary

```ini
[local_groups]
allow = Administrators|Backup Operators|Guests
subject = [ATTENTION] New Local Group Canary Triggered
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified file, you'll recieve an alert email notifying of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated

## Schedule c4N4Re to run at Startup on Linux and Windows

**Windows**
https://www.ionos.com/digitalguide/server/configuration/startup-folder-in-windows-10/

**Linux**
Edit the crontab file with `crontab -e` and add the following:

```bash
@reboot /opt/c4N4Re/c4N4Re.py
```

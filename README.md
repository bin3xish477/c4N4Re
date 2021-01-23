# c4N4Re

**c4N4Re** (pronounced "canary") is a Python program created to easily enable a variety of system canaries. c4N4Re would be perfect to run on a honeypot system but it can also be used on a normal computer where you can track and get alerts when things like CPU and RAM utilization percentages exceed a particular value. 

## Example C4N4Re Alert

![alert_email](/images/c4N4Re_alert_email_ex.png)

## Setup

Installing Python Dependencies for **Windows**:

```
python3 -m pip install -U -r windows_requirements.txt
```

Installing Python Dependencies for **Linux**:

```
python3 -m pip install -U -r linux_requirements.txt
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

The general section found in the `config.ini` has three options that allows you to control some functionality:

```ini
[general]
; the number of seconds to wait before c4N4Re
; checks for any triggered canaries
interval_between_checks = 2
; If this is set to true, you will continue to receive
; alerts from c4N4Re when a canary is triggered 
; as long as it running
; if this is set to false, you will only receive one email
; from c4N4Re when a canary triggered and then c4N4Re will exit.
continue_beyond_initial_alert = true
; the number of alert emails to receive from c4N4Re
; Note: this only applies when `continue_beyond_initial_alert` is set to true
max_alerts = 5
```

### Enabling Canaries

Using c4N4Re is all about the `config.ini` file. Uncommenting any section, excluding the "general" and "smtp_config" sections, will be configured to automatically activate a canary corresponding to the name of that section. 

**CPU Canary**

```ini
[cpu]
max_util = 80.0
subject = [ATTENTION] CPU Utilization Canary Triggered
```

- The `max_util` option specifies the maximum CPU utilization percentage that must be exceeded before c4N4Re to send you an alert email informing you about high CPU utilization percentages.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**RAM Canary**

```ini
[ram]
max_util = 80.0
subject = [ATTENTION] RAM Utilization Canary Triggered
```

- The `max_util` option specifies the maximum RAM utilization percentage that must be exceeded before c4N4Re sends you an alert email informing you about high RAM utilization percentages.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**Storage Disks Canary**

**Note**: currently only works with **Windows**

```ini
[disks]
drives = C:\
max_util = 80.0
subject = [ATTENTION] Disk Utilization Canary Triggered
```

- The `drives` options is where you specify the drive you wish to monitor storage levels.
- The `max_util` option specifies the maximum storage percentage that must be exceeded before c4N4Re sends you an alert email regarding the stats for a drive such as total, used, and available space.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**SSH Canary**

```ini
[ssh]
max_ssh_connections = 1
subject = [ATTENTION] Concurrnt SSH Connection Max Canary Triggered
```

- The `max_ssh_connections` option specifies the maximum number of concurrent SSH connections that must be exceeded before c4N4re sends you an alert email informing you about the number of active SSH connections on the host.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**IP Canary**

```ini
[ip]
subnet_blocklist = 31.33.7.0/24
subject = [ATTENTION] Blacklisted IP Canary Triggered
```

- The `subnet_blocklist` specifies which IP subnet the host is not allowed to communicate with. If c4N4Re finds an IP address being used within the provided subnet, c4N4Re will send an email regarding the IP address it detected.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**Ports Canary**

```ini
[ports]
deny = 22|80
subject = [ATTENTION] Port Canary Triggered
```

- The `deny` options can be used to specify which ports should not be running locally on the host system. If c4N4Re detects that one of these ports are open, c4N4Re will send an alert email regarding the opened port. 
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**File Canary**

**NOTE**: if you wish to use the file canaries on **Linux**, you need to tell the Linux kernal that you want your drives to use `strictatime` as opposed to `relatime`. You can find more information regarding what this does in the following links:

- https://askubuntu.com/questions/985030/mount-with-atime
    
but it pretty much just has to do with the amount of time it takes before the access times for files in Linux get updated.
So, in order to make this change you need to edit your `/etc/fstab` file and add the value `strictatime` to your drives as shown below (You really only need to add this value to the `/` mount point, specifying to main drive):

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

```ini
[files]
monitor = secrets.txt|C:\Users\binexis\important.txt
subject = [Custom subject header for email]
```

- The `monitor` option is where you specify which files you wish to monitor. If anyone opens any one of the specified files, you'll recieve an alert email notifying you of this action. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.


**Process Canary**

```ini
[processes]
monitor = notepad.exe
subject = [ATTENTION] Process Canary Triggered
```

- The `monitor` option allows you to specify which process should not be running on the host. If c4N4Re discovers that a process with a name found in the `monitor` list is running, c4N4Re will send an alert email informing you that that process is running.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**New User Canary**

```ini
[users]
allow = rodri
subject = [ATTENTION] New User Canary Triggered
```

- The `allow` option allows you to specify which users should be on the host. If c4N4Re detects that a new user was created and therefore not in the `allow` list, c4N4Re will send an alert email regarding the newly created user/s.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

**New Local Group Canary**

```ini
[local_groups]
allow = Administrators|Backup Operators|Guests
subject = [ATTENTION] New Local Group Canary Triggered
```

- The `allow` option allows you to specify which local groups should exist on the host. If c4N4Re detects that a new user was create, c4N4Re will send an alert email regarding the newly created group. If this value is set to nothing, for example, `allow = `, c4N4Re will automatically populate this field with all the groups on the system.
- The `subject` option specifies the subject header for the alert email you will recieve if this canary is triggered.

## Run (Must be ran as Administrator !!!)

```
python3 c4N4Re.py
```

## Schedule c4N4Re to run at Startup on Linux and Windows

**Windows**

https://www.codespeedy.com/how-to-run-a-python-file-when-windows-starts/

**Linux**

Edit the crontab file with `crontab -e` and add the following:

```bash
@reboot sudo /opt/c4N4Re/c4N4Re.py
```

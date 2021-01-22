# c4N4Re

**c4N4Re** (pronounced "canary") is a Python program to easily enable a variety of system canaries.

## Setup

Don't forget Linux: `sudo apt install python3-tk`



**Windows**

Installing Python Dependencies:

```
python3 -m pip install -U -r windows_requirements.txt
```

**Linux**

Installing Python Dependencies:

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

## STMP Authentication

c4N4Re will look for the environment variables: `EMAIL_ADDR` and `EMAIL_PASS`', where the former is the email address and the latter is the app password for the specified email address. If you are using Gmail, as most peopele are, it is advised to [create an app password](https://www.lifewire.com/get-a-password-to-access-gmail-by-pop-imap-2-1171882).


## Usage 

**Enabling Canaries**

Using c4N4Re is all about the `config.ini` file. Uncommenting will any section, excluding the "general", will be configured to run automatically activate a canary revelant to the name of that section. For example, setting the activating a file canary for a particular file looks something like this:

```
[files]
monitor = secrets.txt
subject = [Custom subject header for email]
```

- The `monitor` option is where you specify which files you wish to get an alerted upon someone accessing them. This is perfect for creating seemingly lucrative files to lure a hacker to open them, expecting to obtain some valid information.
- The `subject` option is configurable for all canaries that are activated



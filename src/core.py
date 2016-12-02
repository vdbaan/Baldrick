####################################################################################
# Core functions and settings
####################################################################################
from __future__ import print_function
import os
import pwd
import sys
import random
import time
import argparse

# version information
VERSION = "0.0.1"

baldrickName = """
  ____        _     _      _      _
 | __ )  __ _| | __| |_ __(_) ___| | __
 |  _ \ / _` | |/ _` | '__| |/ __| |/ /
 | |_) | (_| | | (_| | |  | | (__|   <
 |____/ \__,_|_|\__,_|_|  |_|\___|_|\_\\

    """

baldrickQuotes = ["With you at the helm, my lord, we cannot lose.",
                  "Not to worry, my Lord; the arrow didn't in fact enter my body.",
                  " I think he looks like a bird who's swallowed a plate, my Lord.",
                  "I think thinking is so important, my Lord.",
                  "Oh, bloody hell!",
                  "Have you got a plan, my lord?",
                  "I am as stupid as I look Sir. But if I can help, I will."]

help = """
Usage: Baldrick [-h] [-n|--nessus FILE [FILE...]] [-m|--nmap FILE [FILE...]] [-o|--openvas FILE [FILE...]] [-v] [-b --uids UIDS --pwds PWDS] [-e]

optional arguments:
  -h                  --help                    Show this help message and exit
  -d                  --debug                   Debug logging
  -n FILE [FILE ...], --nessus FILE [FILE ...]  The nessus report whish will be used as base
  -m FILE [FILE ...], --nmap FILE [FILE ...]    The nmap XML file which will be used as base
  -o FILE [FILE ...], --openvas FILE [FILE ...] The openvas XML report which will be used as base
  -v                  --validate                Run the validation plugins
  -b                  --brute                   Run the brute force plugins. This requires the following two options uid and pwd
                      --uids UIDS               A file containing user names
                      --pwds PWDS               A file containing passwords
  -e,                 --exploit                 Run the exploit plugins
"""

current_milli_time = lambda: int(round(time.time() * 1000))

def getQuote():
    return " -- \"%s\"\n" % (random.choice(baldrickQuotes))

# python 2 compatibility
try: input = raw_input
except NameError: pass

class bcolors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERL = '\033[4m'
    ENDC = '\033[0m'
    backBlack = '\033[40m'
    backRed = '\033[41m'
    backGreen = '\033[42m'
    backYellow = '\033[43m'
    backBlue = '\033[44m'
    backMagenta = '\033[45m'
    backCyan = '\033[46m'
    backWhite = '\033[47m'

# main status calls for print functions
def print_status(message,end='\n'):
    print((bcolors.GREEN) + (bcolors.BOLD) + \
        ("[*] ") + (bcolors.ENDC) + (str(message)),end=end)


def print_info(message):
    print((bcolors.BLUE) + (bcolors.BOLD) + \
        ("[-] ") + (bcolors.ENDC) + (str(message)))


def print_info_spaces(message):
    print((bcolors.BLUE) + (bcolors.BOLD) + \
        ("  [-] ") + (bcolors.ENDC) + (str(message)))


def print_warning(message):
    print((bcolors.YELLOW) + (bcolors.BOLD) + \
        ("[!] ") + (bcolors.ENDC) + (str(message)))


def print_error(message):
    print((bcolors.RED) + (bcolors.BOLD) + \
        ("[!] ") + (bcolors.ENDC) + (bcolors.RED) + \
        (str(message)) + (bcolors.ENDC))

def clear_screen():
    if os.name == 'nt':
       os.system('cls')
    else:
        os.system('clear')

def read_input(message):
    clear_screen()
    print((bcolors.YELLOW) + (bcolors.BOLD) + \
         ("************************************************************************************\n") + \
         (bcolors.ENDC) + (str(message)) +"\n" + (bcolors.YELLOW) + (bcolors.BOLD) + \
         ("************************************************************************************") + \
         (bcolors.ENDC))
    return input()

def checkRoot(args):
    sudo = 0
    if os.getuid() == 0:
        # our user ID is root, so we may have been invoked via sudo
        if 'SUDO_USER' in os.environ:
            username = os.environ['SUDO_USER']
            sudo = 1
        elif 'USER' in os.environ:
            username = os.environ['USER']
        else:
            username = "root"
    else:
        if 'USER' in os.environ:
            username = os.environ['USER']
        else:
            username = pwd.getpwuid(os.getuid()).pw_name
    #Try to get uid and gid from the user name, which may not exist
    try:
        pwd.getpwnam(username)
    except KeyError:
        username = 'root'

    userid = pwd.getpwnam(username).pw_uid
    groupid = pwd.getpwnam(username).pw_gid

    args.groupid=groupid
    args.user=username
    args.userid=userid
    args.sudo=sudo
    if os.geteuid() != 0:
        # print_error("this needs to be run as root. Please sudo it up! Exiting...")
        raise Exception("this needs to be run as root. Please sudo it up! Exiting...")


class MyParser(argparse.ArgumentParser):
     def format_help(self):
         return "%s\n%s\n%s" % (baldrickName, getQuote(),help)
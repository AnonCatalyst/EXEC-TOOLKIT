#!/usr/bin/env python3

import requests
from datetime import datetime
import re
import ipaddress
import argparse

# Color setup
class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


def checkProtonAPIStatut():
    """
    This function check proton API status: ONLINE / OFFLINE
    """
    requestProton_mail_statut = requests.get('https://api.protonmail.ch/pks/lookup?op=index&search=test@protonmail.com')
    if requestProton_mail_statut.status_code == 200:
        print("Protonmail API is " + f"{bcolors.BOLD}ONLINE{bcolors.ENDC}")
    else:
        print("Protonmail API is " + f"{bcolors.BOLD}OFFLINE{bcolors.ENDC}")

    requestProton_vpn_statut = requests.get('https://api.protonmail.ch/vpn/logicals')
    if requestProton_vpn_statut.status_code == 200:
        print("Protonmail VPN is " + f"{bcolors.BOLD}ONLINE{bcolors.ENDC}")
    else:
        print("Protonmail VPN is " + f"{bcolors.BOLD}OFFLINE{bcolors.ENDC}")


def checkValidityOneAccount(email):
    """
    PROGRAM 1 : Test the validity of one ProtonMail account
    """
    regexEmail = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    if re.search(regexEmail, email):
        requestProton = requests.get(f'https://api.protonmail.ch/pks/lookup?op=index&search={email}')
        bodyResponse = requestProton.text

        protonNoExist = "info:1:0"  # not valid
        protonExist = "info:1:1"  # valid

        if protonNoExist in bodyResponse:
            return f"Protonmail email {email} is " + f"{bcolors.FAIL}not valid{bcolors.ENDC}"
        if protonExist in bodyResponse:
            return f"Protonmail email {email} is " + f"{bcolors.OKGREEN}valid{bcolors.ENDC}"
    else:
        return "Invalid email format."


def checkUsernameExistence(username):
    """
    PROGRAM 4 : Check if a username exists on ProtonMail (username@protonmail.com, etc.)
    """
    domainList = ["@protonmail.com", "@protonmail.ch", "@pm.me"]
    valid_usernames = []

    for domain in domainList:
        email = username + domain
        requestProton = requests.get(f'https://api.protonmail.ch/pks/lookup?op=index&search={email}')
        bodyResponse = requestProton.text
        protonNoExist = "info:1:0"  # not valid
        protonExist = "info:1:1"  # valid

        if protonExist in bodyResponse:
            valid_usernames.append(f"{email} is " + f"{bcolors.OKGREEN}valid{bcolors.ENDC}")
        if protonNoExist in bodyResponse:
            valid_usernames.append(f"{email} is " + f"{bcolors.FAIL}not valid{bcolors.ENDC}")

    return valid_usernames


def checkGeneratedProtonAccounts(firstName, lastName, yearOfBirth, pseudo1, pseudo2, zipCode):
    """
    PROGRAM 2 : Try to find if your target has a ProtonMail account by generating multiple addresses by combining information fields inputted
    """
    domainList = ["@protonmail.com", "@protonmail.ch", "@pm.me"]
    pseudoList = []

    for domain in domainList:
        pseudoList.append(firstName + lastName + domain)
        pseudoList.append(lastName + firstName + domain)
        pseudoList.append(firstName[0] + lastName + domain)
        pseudoList.append(pseudo1 + domain)
        pseudoList.append(pseudo2 + domain)
        pseudoList.append(lastName + domain)
        pseudoList.append(firstName + lastName + yearOfBirth + domain)
        pseudoList.append(firstName[0] + lastName + yearOfBirth + domain)
        pseudoList.append(lastName + firstName + yearOfBirth + domain)

    # Remove duplicates and irrelevant combinations
    pseudoList = list(set(pseudoList))

    results = []
    for pseudo in pseudoList:
        requestProton = requests.get(f'https://api.protonmail.ch/pks/lookup?op=index&search={pseudo}')
        bodyResponse = requestProton.text
        protonNoExist = "info:1:0"  # not valid
        protonExist = "info:1:1"  # valid

        if protonExist in bodyResponse:
            results.append(f"{pseudo} is " + f"{bcolors.OKGREEN}valid{bcolors.ENDC}")
        if protonNoExist in bodyResponse:
            results.append(f"{pseudo} is " + f"{bcolors.FAIL}not valid{bcolors.ENDC}")

    return results


def checkIPProtonVPN(ip):
    """
    PROGRAM 3 : Find if your IP is currently affiliated with ProtonVPN
    """
    requestProton_vpn = requests.get('https://api.protonmail.ch/vpn/logicals')
    bodyResponse = requestProton_vpn.text
    if str(ip) in bodyResponse:
        return f"The IP {ip} is currently affiliated with ProtonVPN"
    else:
        return f"The IP {ip} is not affiliated with ProtonVPN."


# Entry point of the script
def main():
    parser = argparse.ArgumentParser(description="ProtonMail and ProtonVPN utilities.")
    
    # Optional arguments with '-' prefix
    parser.add_argument("-e", "--email", help="Email address to check")
    parser.add_argument("-u", "--username", help="Username to check")
    parser.add_argument("-f", "--firstName", help="First name of the target")
    parser.add_argument("-l", "--lastName", help="Last name of the target")
    parser.add_argument("-y", "--yearOfBirth", help="Year of birth")
    parser.add_argument("-p1", "--pseudo1", help="First pseudo")
    parser.add_argument("-p2", "--pseudo2", help="Second pseudo")
    parser.add_argument("-z", "--zipCode", help="Zip code")
    parser.add_argument("-ip", "--ip", help="IP address to check")

    # Parse arguments
    args = parser.parse_args()

    # Call appropriate function based on arguments
    if args.email:
        print(checkValidityOneAccount(args.email))
    elif args.username:
        results = checkUsernameExistence(args.username)
        for result in results:
            print(result)
    elif args.firstName and args.lastName:
        results = checkGeneratedProtonAccounts(args.firstName, args.lastName, args.yearOfBirth, args.pseudo1, args.pseudo2, args.zipCode)
        for result in results:
            print(result)
    elif args.ip:
        print(checkIPProtonVPN(args.ip))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

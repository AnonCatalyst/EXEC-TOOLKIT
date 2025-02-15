#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import platform
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Constants for colors and styles
PRIMARY   = Fore.CYAN
SECONDARY = Fore.YELLOW
ACCENT1   = Fore.GREEN
ACCENT2   = Fore.MAGENTA
ACCENT3   = Fore.RED
ACCENT4   = Fore.WHITE
ACCENT5   = Fore.BLUE

def is_arch_linux():
    """Check if the system is running Arch Linux."""
    try:
        return "arch" in platform.uname().release.lower() or "arch" in platform.system().lower()
    except Exception:
        return False

def get_banner_frames():
    """Generate the banner frames based on OS."""
    if is_arch_linux():
        return [
            f"{ACCENT2}__\n{ACCENT5}        >>> EXECUTION MODULE ONLINE...{Style.RESET_ALL}",
            f"{PRIMARY}__\n{ACCENT3}        >>> SYSTEM READY. AWAITING COMMANDS...{Style.RESET_ALL}"
        ]
    else:
        return [
            f"""{ACCENT2}
██████╗░██╗░░░░░░█████╗░  ███████╗██╗░░██╗███████╗░█████╗░
██╔══██╗██║░░░░░██╔══██╗  ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗
██████╔╝██║░░░░░███████║  █████╗░░░╚███╔╝░█████╗░░██║░░╚═╝
██╔══██╗██║░░░░░██╔══██║  ██╔══╝░░░██╔██╗░██╔══╝░░██║░░██╗
██║░░██║███████╗██║░░██║  ███████╗██╔╝╚██╗███████╗╚█████╔╝
╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝╚══════╝░╚════╝░
{ACCENT5}        >>> EXECUTION MODULE ONLINE... 🌟🚀{Style.RESET_ALL}""",
            f"""{PRIMARY} 
██████╗░██╗░░░░░░█████╗░  ███████╗██╗░░██╗███████╗░█████╗░
██╔══██╗██║░░░░░██╔══██╗  ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗
██████╔╝██║░░░░░███████║  █████╗░░░╚███╔╝░█████╗░░██║░░╚═╝
██╔══██╗██║░░░░░██╔══██║  ██╔══╝░░░██╔██╗░██╔══╝░░██║░░██╗
██║░░██║███████╗██║░░██║  ███████╗██╔╝╚██╗███████╗╚█████╔╝
╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝╚══════╝░╚════╝░
{ACCENT3}        >>> SYSTEM READY. AWAITING COMMANDS... 🎉⚡{Style.RESET_ALL}"""
        ]

def animated_banner():
    """Display an animated banner based on the OS."""
    banner_frames = get_banner_frames()
    for frame in banner_frames:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(frame)
        time.sleep(1.2)
        

def main():
    # Display detected OS and architecture
    os_info = platform.system()
    arch_info = platform.machine()
    print(f"Detected OS: {os_info} - Architecture: {arch_info}")
    animated_banner()  # Show animated startup banner

    # Determine the absolute path to the 'src' directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, 'src')

    if not os.path.isdir(src_dir):
        print("Error: 'src' directory not found. Make sure it exists in the same directory as this script.")
        sys.exit(1)

    # Change working directory to 'src'
    try:
        os.chdir(src_dir)
        print(f"Changed directory to: {os.getcwd()}")
    except Exception as e:
        print(f"Error: Unable to change directory to 'src'. {e}")
        sys.exit(1)

    # Ensure that main.py exists
    if not os.path.isfile('main.py'):
        print("Error: 'main.py' not found in the 'src' directory.")
        sys.exit(1)

    # Additional command-line arguments are passed along to main.py
    command = [sys.executable, 'main.py'] + sys.argv[1:]
    print(f"Executing main.py with command: {' '.join(command)}")

    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Execution of main.py failed with error code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"An unexpected error occurred while executing main.py: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

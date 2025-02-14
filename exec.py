#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def main():
    # Display detected OS and architecture
    os_info = platform.system()
    arch_info = platform.machine()
    print(f"Detected OS: {os_info} - Architecture: {arch_info}")

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

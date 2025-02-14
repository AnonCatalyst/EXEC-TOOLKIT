#!/bin/bash

# Navigate to src directory
cd src || { echo "src directory not found!"; exit 1; }

# Detect the platform
OS=$(uname -s)
ARCH=$(uname -m)

# Function to run Python script
echo "Running main.py..."
if command -v python3 &>/dev/null; then
    python3 main.py
elif command -v python &>/dev/null; then
    python main.py
else
    echo "Python is not installed! Installing..."
    case "$OS" in
        Linux*)
            if [ -f "/etc/debian_version" ]; then
                sudo apt update && sudo apt install -y python3
            elif [ -f "/etc/arch-release" ]; then
                sudo pacman -Sy --noconfirm python
            elif [ -f "/etc/os-release" ] && grep -qi "kali" /etc/os-release; then
                sudo apt update && sudo apt install -y python3
            fi
            ;;
        Darwin*)
            brew install python
            ;;
        MINGW*|CYGWIN*|MSYS*)
            choco install python
            ;;
        Android*)
            pkg install python
            ;;
        *)
            echo "Unsupported OS"
            exit 1
            ;;
    esac
    python3 main.py
fi

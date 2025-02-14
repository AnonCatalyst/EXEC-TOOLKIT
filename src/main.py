import sys
import subprocess
import time
import signal
import os
import platform
import multiprocessing
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

# Exit flag for handling clean exit
exit_flag = multiprocessing.Event()

def clean_exit(signum, frame):
    print(ACCENT3 + "\nExiting RLA EXEC...")
    exit_flag.set()
    sys.exit(0)

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

def execute_script(script, description, query, num_results=None, use_proxy=None,
                   country_file=None, language_file=None, date_range_file=None,
                   output_file=None, include_num_results=True):
    """
    Execute the selected script with provided arguments.
    If output_file is provided (or set to True), capture the script's output, print it,
    and save it to that file.
    """
    args = ["python", script, query]
    
    # Only include num_results if include_num_results is True and a value is provided.
    if include_num_results and num_results is not None:
        args.append(num_results)
    if use_proxy is not None:
        args.append('y' if use_proxy else 'n')
    if country_file:
        args.append(country_file)
    if language_file:
        args.append(language_file)
    if date_range_file:
        args.append(date_range_file)

    msg = f"Running {description} with query '{query}'"
    if include_num_results and num_results:
        msg += f" and {num_results} results..."
    else:
        msg += "..."
    print(SECONDARY + msg)
    
    # If output_file is True, assign a default file path.
    if output_file is True:
        default_folder = "../RESULTS"
        if not os.path.exists(default_folder):
            os.makedirs(default_folder)
        output_file = os.path.join(default_folder, os.path.splitext(script)[0] + ".txt")
    
    try:
        if output_file:
            # Capture output so we can both display and save it.
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            print(result.stdout)
            with open(output_file, "w") as f:
                f.write(result.stdout)
            print(SECONDARY + f"{description} executed successfully. Output saved to {output_file}.")
        else:
            result = subprocess.run(args, text=True, check=True)
            print(SECONDARY + f"{description} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(ACCENT3 + f"[ERROR] Execution failed: {e}")

def update_file(file_path):
    """
    Show current file contents (if any) and ask the user whether to update it.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            current_content = f.read().strip()
        prompt_str = (f"{Fore.CYAN}+{Fore.GREEN} Current content of {file_path}: {Fore.CYAN}{current_content}{Fore.RESET}\n"
                      f"{Fore.GREEN}Do you want to update {file_path}? (y/n):{Fore.RESET} ")
    else:
        prompt_str = (f"{file_path} does not exist. It will be created.\n"
                      f"{Fore.GREEN}Do you want to update {file_path}? (y/n):{Fore.RESET} ")

    choice = input(ACCENT1 + prompt_str).strip().lower()
    if choice in ['y', 'yes']:
        new_content = input(ACCENT1 + f"Enter new content for {file_path}: ").strip()
        if new_content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(SECONDARY + f"{file_path} updated successfully.")
        else:
            print(SECONDARY + "No content provided. File not updated.")
    else:
        print(SECONDARY + f"{file_path} not updated.")

def get_user_inputs(ask_for_num_results=True, ask_for_files=False):
    query = input(ACCENT1 + "Enter the search query: ").strip()
    with open("config/query.txt", "w") as f:
        f.write(query)
    
    num_results = None
    if ask_for_num_results:
        num_results = input(ACCENT1 + "Enter number of results (default: 10): ").strip() or "10"
    
    country_file = language_file = date_range_file = None
    if ask_for_files:
        country_file    = "config/country.txt"
        language_file   = "config/language.txt"
        date_range_file = "config/date_range.txt"
        update_file(country_file)
        update_file(language_file)
        update_file(date_range_file)
    
    return query, num_results, country_file, language_file, date_range_file

def main():
    signal.signal(signal.SIGINT, clean_exit)  # Handle CTRL+C
    animated_banner()  # Show animated startup banner

    options = {
        "1": ("search.py", "Web Search"),
        "2": ("backrooms.py", "Deep Web Search"),
        "3": ("domainbox.py", "Domain Query Enrichment"),
        "4": ("userdash.py", "Username Search"),
        "5": ("Complete Execution", "Complete Execution"),
        "0": ("Exit", "Exit RLA EXEC")
    }

    while not exit_flag.is_set():
        print(PRIMARY + "\nSelect an option:")
        for key, value in options.items():
            print(ACCENT2 + f"{key}: {value[1]}")

        choice = input(ACCENT5 + "\n>>> Select option: ").strip()
        if choice == "0":
            clean_exit(None, None)

        if choice == "5":
            # Complete Execution: prompt for inputs with file updates.
            query, num_results, country_file, language_file, date_range_file = get_user_inputs(True, True)
            # Create RESULTS folder for scripts that capture output.
            results_folder = "../RESULTS"
            os.makedirs(results_folder, exist_ok=True)
            for key in options:
                if key in ["5", "0"]:
                    continue
                script, description = options[key]
                # For all scripts except domainbox.py, build an output file.
                if script != "domainbox.py":
                    result_filename = os.path.splitext(script)[0] + ".txt"
                    output_file = os.path.join(results_folder, result_filename)
                else:
                    output_file = None  # For domainbox.py, use the option 3 behavior.
                
                if script == "backrooms.py":
                    use_proxy_val = True
                    execute_script(script, description, query, num_results, use_proxy_val,
                                   None, None, None, output_file)
                else:
                    # For domainbox.py (option 3) and userdash.py, ignore file arguments.
                    if script in ["domainbox.py", "userdash.py"]:
                        country_file = language_file = date_range_file = None
                    # For domainbox.py, execute just like option 3.
                    if script == "domainbox.py":
                        execute_script(script, description, query,
                                       None,       # num_results
                                       None,       # use_proxy
                                       None,       # country_file
                                       None,       # language_file
                                       None,       # date_range_file
                                       True,       # output_file (now a flag to capture output)
                                       include_num_results=False)
                    else:
                        execute_script(script, description, query, num_results, None,
                                       country_file, language_file, date_range_file, output_file)
        elif choice == "1":
            # Option 1: Web Search with file updates.
            query, num_results, country_file, language_file, date_range_file = get_user_inputs(True, True)
            script, description = options[choice]
            execute_script(script, description, query, num_results, None,
                           country_file, language_file, date_range_file)
        elif choice in options:
            # Options 2, 3, and 4: no file updates.
            script, description = options[choice]
            if script == "backrooms.py":
                use_proxy_input = input(ACCENT1 + "Do you want to use a proxy? (y/n): ").strip().lower()
                use_proxy = use_proxy_input in ['y', 'yes']
            else:
                use_proxy = None
            query, num_results, country_file, language_file, date_range_file = get_user_inputs(True, False)
            if script in ["backrooms.py", "omainbox.py", "userdash.py"]:
                country_file = language_file = date_range_file = None
            if script == "domainbox.py":
                execute_script(script, description, query,
                               None,       # num_results
                               None,       # use_proxy
                               None,       # country_file
                               None,       # language_file
                               None,       # date_range_file
                               True,       # output_file flag set to True for capturing output
                               include_num_results=False)
            else:
                execute_script(script, description, query, num_results, use_proxy,
                               country_file, language_file, date_range_file)
    
if __name__ == "__main__":
    main()

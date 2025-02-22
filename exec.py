import os
import sys
import runpy
from colorama import init, Fore, Style
from src.help import show_help  # Importing the show_help function from help.py

# Initialize colorama for colorful output
init(autoreset=True)

def execute_command(module_path, args):
    """
    Executes a Python module (script) by setting sys.argv appropriately and running it with runpy.
    This avoids spawning a subprocess and works across platforms.
    """
    # Backup the original sys.argv so it can be restored later.
    old_argv = sys.argv.copy()
    sys.argv = [module_path] + args
    try:
        print(f"{Fore.GREEN}[INFO] Running command: {module_path} {Style.RESET_ALL}")
        runpy.run_path(module_path, run_name="__main__")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Command failed: {e}{Style.RESET_ALL}")
    finally:
        sys.argv = old_argv

# Show help message if -h or --help is provided
if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
    show_help()  # Call the function from help.py
    sys.exit(0)

# Check if user provided at least one argument
if len(sys.argv) < 2:
    print(f"{Fore.RED}Error: Missing argument. Use -h or --help for more information.{Fore.RESET}")
    sys.exit(1)

# Debug: print the received command.
command = sys.argv[1]
print(f"DEBUG: Command received is '{command}'")

if command == "-depth":
    if len(sys.argv) > 3:
        query, num_results = sys.argv[2], sys.argv[3]
        print(f"{Fore.CYAN}DEPTH SEARCH | Executing deep web search for: {Fore.GREEN}{query}{Fore.CYAN} with {Fore.GREEN}{num_results} results{Fore.RESET}")
        execute_command("src/depthsearch.py", [query, num_results])
    else:
        print(f"{Fore.RED}Error: Please provide a query and number of results after -depth.{Fore.RESET}")
        sys.exit(1)

elif command == "-dbox":
    if len(sys.argv) > 2:
        username = sys.argv[2]
        print(f"{Fore.CYAN}Executing domain box query for: {Fore.GREEN}{username}{Fore.RESET}")
        execute_command("src/domainbox.py", [username])
    else:
        print(f"{Fore.RED}Error: Please provide a username after -dbox.{Fore.RESET}")
        sys.exit(1)

elif command in ("-owl", "--socialowl"):
    if len(sys.argv) > 2:
        username = sys.argv[2]
        print(f"{Fore.CYAN}Executing social owl search for: {Fore.GREEN}{username}{Fore.RESET}")
        execute_command("src/owl.py", [username])
    else:
        print(f"{Fore.RED}Error: Please provide a username after {command}.{Fore.RESET}")
        sys.exit(1)

elif command == "-webuser":
    if len(sys.argv) > 2:
        username = sys.argv[2]
        proxy_file = None
        num_results = "30"  # Default value

        # Check for optional flags
        if "-prox" in sys.argv:
            prox_index = sys.argv.index("-prox")
            if prox_index + 1 < len(sys.argv) and not sys.argv[prox_index + 1].startswith("-"):
                proxy_file = sys.argv[prox_index + 1]
            else:
                proxy_file = "proxies.txt"  # Default file if -prox is used without an argument

        if "-n" in sys.argv:
            n_index = sys.argv.index("-n")
            if n_index + 1 < len(sys.argv) and sys.argv[n_index + 1].isdigit():
                num_results = sys.argv[n_index + 1]

        print(f"{Fore.CYAN}Executing web search for username: {Fore.GREEN}{username}{Fore.CYAN} with {Fore.GREEN}{num_results} results{Fore.RESET}")
        args = [username, "-n", num_results]
        if proxy_file:
            print(f"{Fore.YELLOW}[INFO] Using proxy file: {proxy_file}{Fore.RESET}")
            args += ["-prox", proxy_file]

        execute_command("src/webuser.py", args)
    else:
        print(f"{Fore.RED}Error: Please provide a username after -webuser.{Fore.RESET}")
        sys.exit(1)

elif command == "-websearch":
    if len(sys.argv) > 2:
        # Join the remaining arguments after the command as a single query string (to handle spaces)
        query = " ".join(sys.argv[2:])
        proxy_file = None
        num_results = "30"  # Default value
        language = None
        date_range = None
        country = None

        # Check for optional flags
        if "-prox" in sys.argv:
            prox_index = sys.argv.index("-prox")
            if prox_index + 1 < len(sys.argv) and not sys.argv[prox_index + 1].startswith("-"):
                proxy_file = sys.argv[prox_index + 1]
            else:
                proxy_file = "proxies.txt"

        if "-n" in sys.argv:
            n_index = sys.argv.index("-n")
            if n_index + 1 < len(sys.argv) and sys.argv[n_index + 1].isdigit():
                num_results = sys.argv[n_index + 1]

        if "-l" in sys.argv:
            l_index = sys.argv.index("-l")
            if l_index + 1 < len(sys.argv):
                language = sys.argv[l_index + 1]

        if "-d" in sys.argv:
            d_index = sys.argv.index("-d")
            if d_index + 1 < len(sys.argv):
                date_range = sys.argv[d_index + 1]

        if "-c" in sys.argv:
            c_index = sys.argv.index("-c")
            if c_index + 1 < len(sys.argv):
                country = sys.argv[c_index + 1]

        print(f"{Fore.CYAN}Executing web search for query: {Fore.GREEN}{query}{Fore.CYAN} with {Fore.GREEN}{num_results} results{Fore.RESET}")
        
        # Prepare the argument list for the target module
        args = [query, "-n", num_results]
        if proxy_file:
            print(f"{Fore.YELLOW}[INFO] Using proxy file: {proxy_file}{Fore.RESET}")
            args += ["-prox", proxy_file]
        if language:
            print(f"{Fore.YELLOW}[INFO] Using language: {language}{Fore.RESET}")
            args += ["-l", language]
        if date_range:
            print(f"{Fore.YELLOW}[INFO] Using date range: {date_range}{Fore.RESET}")
            args += ["-d", date_range]
        if country:
            print(f"{Fore.YELLOW}[INFO] Using country: {country}{Fore.RESET}")
            args += ["-c", country]

        execute_command("src/websearch.py", args)
    else:
        print(f"{Fore.RED}Error: Please provide a query after -websearch.{Fore.RESET}")
        sys.exit(1)

elif command == "-proton":
    if len(sys.argv) > 2:
        args = []
        if "-e" in sys.argv:
            e_index = sys.argv.index("-e")
            if e_index + 1 < len(sys.argv):
                args += ["-e", sys.argv[e_index + 1]]
        if "-u" in sys.argv:
            u_index = sys.argv.index("-u")
            if u_index + 1 < len(sys.argv):
                args += ["-u", sys.argv[u_index + 1]]
        if "-f" in sys.argv:
            f_index = sys.argv.index("-f")
            if f_index + 1 < len(sys.argv):
                args += ["-f", sys.argv[f_index + 1]]
        if "-l" in sys.argv:
            l_index = sys.argv.index("-l")
            if l_index + 1 < len(sys.argv):
                args += ["-l", sys.argv[l_index + 1]]
        if "-y" in sys.argv:
            y_index = sys.argv.index("-y")
            if y_index + 1 < len(sys.argv):
                args += ["-y", sys.argv[y_index + 1]]
        if "-p1" in sys.argv:
            p1_index = sys.argv.index("-p1")
            if p1_index + 1 < len(sys.argv):
                args += ["-p1", sys.argv[p1_index + 1]]
        if "-p2" in sys.argv:
            p2_index = sys.argv.index("-p2")
            if p2_index + 1 < len(sys.argv):
                args += ["-p2", sys.argv[p2_index + 1]]
        if "-z" in sys.argv:
            z_index = sys.argv.index("-z")
            if z_index + 1 < len(sys.argv):
                args += ["-z", sys.argv[z_index + 1]]
        if "-ip" in sys.argv:
            ip_index = sys.argv.index("-ip")
            if ip_index + 1 < len(sys.argv):
                args += ["-ip", sys.argv[ip_index + 1]]

        if not args:
            print(f"{Fore.RED}Error: Please provide at least one option after -proton.{Fore.RESET}")
            sys.exit(1)
        
        print(f"{Fore.CYAN}Executing ProtonGate utility with the following arguments:{Fore.RESET}")
        print(" ".join(args))
        execute_command("src/protongate.py", args)
    else:
        print(f"{Fore.RED}Error: Please provide arguments for -proton.{Fore.RESET}")
        sys.exit(1)

elif command == "-proxysponge":
    proxy_sources = []
    if len(sys.argv) == 2:
        print(f"{Fore.CYAN}Executing ProxySponge to get proxies...{Fore.RESET}")
        execute_command("src/proxysponge.py", proxy_sources)
    elif len(sys.argv) > 2:
        if "-c" in sys.argv or "--check" in sys.argv:
            print(f"{Fore.CYAN}Executing ProxySponge with validation enabled...{Fore.RESET}")
            proxy_sources.append("-c")
        if "-p" in sys.argv or "--proxies" in sys.argv:
            proxy_file_index = sys.argv.index("-p") if "-p" in sys.argv else sys.argv.index("--proxies")
            try:
                proxy_file = sys.argv[proxy_file_index + 1]
                print(f"{Fore.CYAN}Executing ProxySponge with proxy file: {proxy_file}{Fore.RESET}")
                proxy_sources.extend(["-p", proxy_file])
            except IndexError:
                print(f"{Fore.RED}Error: Missing proxy file after -p/--proxies option.{Fore.RESET}")
                sys.exit(1)
        execute_command("src/proxysponge.py", proxy_sources)
    else:
        print(f"{Fore.RED}Error: Please provide arguments for -proxysponge.{Fore.RESET}")
        sys.exit(1)

elif command == "-webdiver":
    if len(sys.argv) > 2:
        url = sys.argv[2]
        output_dir = None

        # Check for optional flags
        if "--output" in sys.argv:
            output_index = sys.argv.index("--output")
            if output_index + 1 < len(sys.argv):
                output_dir = sys.argv[output_index + 1]
            else:
                print(f"{Fore.RED}Error: Missing output directory after --output.{Fore.RESET}")
                sys.exit(1)

        print(f"{Fore.CYAN}Executing web crawler for URL: {Fore.GREEN}{url}{Fore.RESET}")

        args = [url]
        if output_dir:
            print(f"{Fore.YELLOW}[INFO] Saving results to directory: {output_dir}{Fore.RESET}")
            args += ["--output", output_dir]

        execute_command("src/webdiver.py", args)
    else:
        print(f"{Fore.RED}Error: Please provide a URL after -webdiver.{Fore.RESET}")
        sys.exit(1)

else:
    print(f"{Fore.RED}Error: Unknown command '{command}'. Use -h or --help for usage instructions.{Fore.RESET}")
    sys.exit(1)

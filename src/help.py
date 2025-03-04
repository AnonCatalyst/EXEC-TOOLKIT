from colorama import Fore, Style, init
import platform
import os
import time

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
████████████████████████████████████████████████████████████████
█▌▄▄▄ .▐▄• ▄ ▄▄▄ . ▄▄·     ▄▄▄▄▄            ▄▄▌  ▄ •▄ ▪  ▄▄▄▄▄▐█
█▌▀▄.▀· █▌█▌▪▀▄.▀·▐█ ▌▪    •██  ▪     ▪     ██•  █▌▄▌▪██ •██  ▐█
█▌▐▀▀▪▄ ·██· ▐▀▀▪▄██ ▄▄     ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▐▀▀▄·▐█· ▐█.▪▐█
█▌▐█▄▄▌▪▐█·█▌▐█▄▄▌▐███▌     ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█.█▌▐█▌ ▐█▌·▐█
█▌ ▀▀▀ •▀▀ ▀▀ ▀▀▀ ·▀▀▀      ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀ ·▀  ▀▀▀▀ ▀▀▀ ▐█
████████████████████████████████████████████████████████████████
________________________________________________________________
{ACCENT5}          >>> EXECUTION MODULE ONLINE... 🌟🚀{Style.RESET_ALL}""",
            f"""{PRIMARY} 
████████████████████████████████████████████████████████████████
█▌▄▄▄ .▐▄• ▄ ▄▄▄ . ▄▄·     ▄▄▄▄▄            ▄▄▌  ▄ •▄ ▪  ▄▄▄▄▄▐█
█▌▀▄.▀· █▌█▌▪▀▄.▀·▐█ ▌▪    •██  ▪     ▪     ██•  █▌▄▌▪██ •██  ▐█
█▌▐▀▀▪▄ ·██· ▐▀▀▪▄██ ▄▄     ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▐▀▀▄·▐█· ▐█.▪▐█
█▌▐█▄▄▌▪▐█·█▌▐█▄▄▌▐███▌     ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█.█▌▐█▌ ▐█▌·▐█
█▌ ▀▀▀ •▀▀ ▀▀ ▀▀▀ ·▀▀▀      ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀ ·▀  ▀▀▀▀ ▀▀▀ ▐█
████████████████████████████████████████████████████████████████
________________________________________________________________
{ACCENT3}          >>> SYSTEM READY. AWAITING COMMANDS... 🎉⚡{Style.RESET_ALL}"""
        ]

def animated_banner():
    """Display an animated banner based on the OS."""
    banner_frames = get_banner_frames()
    for frame in banner_frames:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(frame)
        time.sleep(1.2)
        

def show_help():
    # Display detected OS and architecture
    os_info = platform.system()
    arch_info = platform.machine()
    print(f"Detected OS: {os_info} - Architecture: {arch_info}")
    animated_banner()  # Show animated startup banner
    print(f"""
{Fore.MAGENTA}[{Fore.CYAN}RLA-EXEC TOOLKIT{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET} YOUR {Fore.MAGENTA}#{Fore.CYAN}1 {Fore.RESET}OSINT TOOLKIT{Fore.RED}!{Fore.RESET}  
    {Fore.BLUE}Options{Fore.RED}:{Fore.RESET}
   -h, --help     Show this help message and exit.
    
{Fore.MAGENTA}[{Fore.CYAN}DEEP WEB SEARCH{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET} USERDEPTH
     Usage: -depth [query] [number]   Execute deep web search for the provided query and number of results.
   Example: python3 exec.py -depth hireahacker 15
    
{Fore.MAGENTA}[{Fore.CYAN}USERNAME OSINT{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET} SOCIAL OWL
  {Fore.BLUE}Configuration Options{Fore.RED}:{Fore.RESET}
  -f FILE, --file FILE   The path to the file containing the list of social media platforms (default: 'social.txt').
   
   {Fore.BLUE}Options{Fore.RED}:{Fore.RESET}
  -owl or --socialowl [username] --pdf  Execute a username search for the provided username.
     Usage: python3 exec.py -owl [username]   or   python3 exec.py --socialowl [username]
   Example: python3 exec.py -owl johndoe --pdf

  -webuser [username] [-prox [proxy_file]] [-n num_results]   Search for a username on multiple search engines.
     Usage: python3 exec.py -webuser johndoe -n 50
   Example: python3 exec.py -webuser johndoe -prox proxies.txt -n 30

{Fore.MAGENTA}[{Fore.CYAN}WEB SEARCH{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET} WEBHUNT0R
   {Fore.BLUE}Options{Fore.RED}:{Fore.RESET}
  -websearch [query] [-prox [proxy_file]] [-n num_results] [-l language] [-d date_range] [-c country]   
     Search for a query or username across multiple search engines with additional options.
    Usage: python3 exec.py -websearch [query] [-prox [proxy_file]] [-n num_results] [-l language] [-d date_range] [-c country]
  Example: python3 exec.py -websearch "john doe" -n 30
  Example: python3 exec.py -websearch "john doe" -n 30 -prox
  Example: python3 exec.py -websearch "john doe" -n 30 -prox proxies.txt
  Example: python3 exec.py -websearch "john doe" -n 30 -l en -c US
  Example: python3 exec.py -websearch "donald trump" -n 50 -prox proxies.txt -l fr -d 2020-2025

{Fore.MAGENTA}[{Fore.CYAN}DOMAIN OSINT{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET} DOMAINBOX & WEBDIVER
   {Fore.BLUE}Options{Fore.RED}:{Fore.RESET}
   -dbox [username]   Execute domain query enrichment for the provided username.
   
   -webdiver [url]    Execute website crawling for the provided URL. Use --output to specify the directory to save results.
     Usage: python3 exec.py -webdiver [url] --output [directory]
   Example: python3 exec.py -webdiver https://example.com --output /path/to/save/results

{Fore.MAGENTA}[{Fore.CYAN}PROTONMAIL AND PROTONVPN UTILITIES{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET}
  Example: python3 exec.py -proton -e johndoe@example.com
   {Fore.BLUE}Options{Fore.RED}:{Fore.RESET}
  -e EMAIL, --email EMAIL               Valid Proton email address check
  -u USERNAME, --username USERNAME      Username to check on Proton
  -f FIRSTNAME, --firstName FIRSTNAME   First name of the target
  -l LASTNAME, --lastName LASTNAME      Last name of the target
  -y YEAROFBIRTH, --yearOfBirth YEAROFBIRTH  Year of birth
  -p1 PSEUDO1, --pseudo1 PSEUDO1        First pseudo
  -p2 PSEUDO2, --pseudo2 PSEUDO2        Second pseudo
  -z ZIPCODE, --zipCode ZIPCODE         Zip code
  -ip IP, --ip IP                       Valid ProtonVPN IP address check
   Example: python3 exec.py -proton -e johndoe@example.com -u johndoe -f John -l Doe -y 1985 -p1 hacker -p2 ghost -z 12345 -ip 192.168.1.1

{Fore.MAGENTA}[{Fore.CYAN}PROXY UTILITIES{Fore.MAGENTA}]{Fore.RED}:{Fore.RESET} SPROXYSPONGE
   {Fore.BLUE}Options{Fore.RED}:{Fore.RESET}
  -proxysponge    Scrape and validate proxies.
    Usage: python3 exec.py -proxysponge
    Example: python3 exec.py -proxysponge

  -proxysponge -p [proxy_file]   Validate proxies from a custom file.
    Usage: python3 exec.py -proxysponge -p proxies.txt
    Example: python3 exec.py -proxysponge -p proxies.txt

  -proxysponge -c   Enable proxy validation while scraping.
    Usage: python3 exec.py -proxysponge -c
    Example: python3 exec.py -proxysponge -c
    """)


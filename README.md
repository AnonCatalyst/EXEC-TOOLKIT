
### RLA-EXEC TOOLKIT v1.2
> REPLACEMENT FOR OMINIS-OSINT ...
**MAKE YOUR OSINT LIFE EASIER - THE FORGER IS FORMING A BETTER OMINIS-OSINT, THROUGH UPDATES THIS TOOL WILL HAVE EVERYTHING OMINIS-OSINT HAS AND MORE!**

## IN-DEVELOPMENT UPDATE: v1.3
**AUTO DEFACE/VULNSCANNER**

## COMMING-NEXT: 
- **1 SQLI VULN SCANNER** > v1.4
- **2 XSS VULN SCANNERS** > v1.5
- **3 INPUT MENU OPTION** > v1.6 
- **GUI OPTIONS** > v1.7
- **WEB UI** > v1.8

![RLA EXEC Multi Tool SCREENSHOT](screenshot/Screenshot_2025-02-17_13-48-27.png)

# RUN OPTIONS:

- ``pip install -r requirements.txt --break-system-packages && cd RLA-EXEC``
- ``python3 exec.py -h``

### > **RLA EXEC ARG VERSION DISPLAY:**
 
```
██████╗░██╗░░░░░░█████╗░  ███████╗██╗░░██╗███████╗░█████╗░
██╔══██╗██║░░░░░██╔══██╗  ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗
██████╔╝██║░░░░░███████║  █████╗░░░╚███╔╝░█████╗░░██║░░╚═╝
██╔══██╗██║░░░░░██╔══██║  ██╔══╝░░░██╔██╗░██╔══╝░░██║░░██╗
██║░░██║███████╗██║░░██║  ███████╗██╔╝╚██╗███████╗╚█████╔╝
╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝╚══════╝░╚════╝░
        >>> SYSTEM READY. AWAITING COMMANDS... 🎉⚡

[RLA-EXEC TOOLKIT]: YOUR #1 OSINT TOOLKIT!  
    Options:
   -h, --help     Show this help message and exit.
    
[DEEP WEB SEARCH]: USERDEPTH
     Usage: -depth [query] [number]   Execute deep web search for the provided query and number of results.
   Example: python3 exec.py -depth hireahacker 15
    
[USERNAME OSINT]: SOCIAL OWL
  Configuration Options:
  -f FILE, --file FILE   The path to the file containing the list of social media platforms (default: 'social.txt').
   
   Options:
  -owl or --socialowl [username] --pdf  Execute a username search for the provided username.
     Usage: python3 exec.py -owl [username]   or   python3 exec.py --socialowl [username]
   Example: python3 exec.py -owl johndoe --pdf

  -webuser [username] [-prox [proxy_file]] [-n num_results]   Search for a username on multiple search engines.
     Usage: python3 exec.py -webuser johndoe -n 50
   Example: python3 exec.py -webuser johndoe -prox proxies.txt -n 30

[WEB SEARCH]: WEBHUNT0R
   Options:
  -websearch [query] [-prox [proxy_file]] [-n num_results] [-l language] [-d date_range] [-c country] 
```
    

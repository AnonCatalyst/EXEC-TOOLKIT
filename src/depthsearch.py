import sys
import requests
from bs4 import BeautifulSoup
import os
import time
import random
from fake_useragent import UserAgent
import platform
import psutil
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class ConsoleConfig:
    BOLD = Style.BRIGHT
    END = Style.RESET_ALL

class Config:
    ERROR_CODE = -1
    SUCCESS_CODE = 0
    MIN_DATA_RETRIEVE_LENGTH = 1
    USE_PROXY = True  # Always use proxy

    SEARCH_ENGINE_URL = "https://ahmia.fi/search/?q="
    PROXY_API_URLS = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite",
        "https://proxyscrape.com/free-proxy-list",
        "https://advanced.name/freeproxy"
    ]

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.update_proxies()

    def update_proxies(self):
        all_proxies = set()
        for url in Config.PROXY_API_URLS:
            try:
                response = requests.get(url)
                response.raise_for_status()
                all_proxies.update(line.strip() for line in response.text.splitlines() if line.strip())
            except requests.RequestException as e:
                print(f"[!] Error fetching proxies from {url}: {e}")
        self.proxies = ["http://" + proxy for proxy in all_proxies]

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None

class DepthSearch:
    def __init__(self):
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self.proxy_manager = ProxyManager()

    def search(self, query, amount):
        headers = {'User-Agent': self.user_agent.random}
        results_found = 0
        proxies_used = 0

        while results_found < amount:
            proxy = self.proxy_manager.get_random_proxy()
            if proxy:
                print(f"{ConsoleConfig.BOLD}{Fore.MAGENTA}Using Proxy:{Fore.CYAN} {proxy}{ConsoleConfig.END}\n")
                self.session.proxies.update({"http": proxy})

            try:
                response = self.session.get(Config.SEARCH_ENGINE_URL + query, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find(id='ahmiaResultsPage')
                result_items = results.find_all('li', class_='result')

                # If no results found, print message and exit
                if not result_items:
                    print(f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}No results found, exiting.{ConsoleConfig.END}")
                    sys.exit(Config.SUCCESS_CODE)  # Exit if no results

                titles = [item.find('p').text if item.find('p') else None for item in result_items]
                urls = [item.find('cite').text if item.find('cite') else None for item in result_items]

                if len(urls) >= Config.MIN_DATA_RETRIEVE_LENGTH:
                    for i in range(len(urls)):
                        url = urls[i]
                        title = titles[i] if i < len(titles) else None

                        # Print results with multiple colors in one line
                        output = f"{ConsoleConfig.BOLD}{Fore.LIGHTGREEN_EX}URL:{Fore.WHITE} {url}\n"
                        if title:
                            output += f"\t{ConsoleConfig.BOLD}Title:{Fore.LIGHTBLUE_EX} {title}\n"
                        output += ConsoleConfig.END
                        print(output, end="")  # `end=""` prevents extra newline, just prints the result
                        results_found += 1
                        if results_found >= amount:
                            break
                else:
                    print(f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}No results found.{ConsoleConfig.END}")

                time.sleep(random.uniform(1, 3))
                proxies_used += 1
                if proxies_used >= len(self.proxy_manager.proxies):
                    print(f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}Ran out of proxies.{ConsoleConfig.END}")
                    break

            except requests.RequestException as e:
                print(f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}Request failed: {e}{ConsoleConfig.END}")
                self.proxy_manager.update_proxies()

        if results_found < amount:
            print(f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}Not enough results found after using all proxies.{ConsoleConfig.END}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"{ConsoleConfig.BOLD}{Fore.RED}Usage: python userdepth.py <query> <num_results>{ConsoleConfig.END}")
        sys.exit(Config.ERROR_CODE)

    query = sys.argv[1]
    try:
        amount = int(sys.argv[2])
    except ValueError:
        print(f"{ConsoleConfig.BOLD}{Fore.RED}Error: Number of results must be an integer.{ConsoleConfig.END}")
        sys.exit(Config.ERROR_CODE)

    print(f"{ConsoleConfig.BOLD}Searching For:{Fore.GREEN} {query} and showing {amount} results...\n{ConsoleConfig.END}")
    searcher = DepthSearch()
    searcher.search(query, amount)

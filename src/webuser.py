import argparse
import os
import random
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

def mimic_human_delay(min_delay=1.0, max_delay=3.0, desc="Waiting"):
    """Sleep for a random amount of time to mimic human behavior with a progress bar."""
    delay = random.uniform(min_delay, max_delay)
    with tqdm(total=delay, bar_format="{l_bar}{bar} {remaining}s", colour="cyan") as pbar:
        for _ in range(int(delay * 10)):  # Updates in 0.1s increments
            time.sleep(0.1)
            pbar.update(0.1)
    print(f"{Fore.GREEN}[INFO]{Fore.YELLOW} {desc} completed after {Fore.CYAN}{delay:.2f}{Fore.YELLOW} seconds.{Style.RESET_ALL}")

def get_random_headers():
    """Generate random headers using Fake UserAgent."""
    ua = UserAgent()
    return {'User-Agent': ua.random}

def search_engine_request(url, params, proxies, engine_name):
    """Generic function to perform a search request with tqdm tracking."""
    mimic_human_delay(desc=f"Preparing {engine_name} search")
    proxy = random.choice(proxies) if proxies else None
    proxy_dict = {"http": proxy, "https": proxy} if proxy else None
    try:
        response = requests.get(url, params=params, headers=get_random_headers(), proxies=proxy_dict)
        return response
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {engine_name} request failed: {e}{Style.RESET_ALL}")
        return None

def duckduckgo_search(query, max_results=30, proxies=None):
    """Perform a DuckDuckGo search."""
    print(f"{Fore.CYAN}[INFO] Searching DuckDuckGo for '{query}'...{Style.RESET_ALL}")
    base_url = "https://duckduckgo.com/html/"
    params = {'q': query}
    results = []

    with tqdm(total=max_results, desc="DuckDuckGo Progress", colour="yellow") as pbar:
        while len(results) < max_results:
            response = search_engine_request(base_url, params, proxies, "DuckDuckGo")
            if not response:
                break
            soup = BeautifulSoup(response.text, "html.parser")
            page_links = [a.get('href') for a in soup.find_all("a", class_="result__a") if a.get('href')]
            results.extend(page_links[:max_results - len(results)])
            pbar.update(len(page_links))
            break  # DuckDuckGo does not support pagination with this method
    return results[:max_results]

def bing_search(query, max_results=30, proxies=None):
    """Perform a Bing search."""
    print(f"{Fore.CYAN}[INFO] Searching Bing for '{query}'...{Style.RESET_ALL}")
    base_url = "https://www.bing.com/search"
    results = []

    with tqdm(total=max_results, desc="Bing Progress", colour="blue") as pbar:
        for start in range(0, max_results, 10):
            params = {'q': query, 'first': start}
            response = search_engine_request(base_url, params, proxies, "Bing")
            if not response:
                break
            soup = BeautifulSoup(response.text, "html.parser")
            page_links = [a.get('href') for a in soup.find_all("a") if a.get('href') and 'http' in a.get('href')]
            results.extend(page_links[:max_results - len(results)])
            pbar.update(len(page_links))
            if len(results) >= max_results:
                break
    return results[:max_results]

def startpage_search(query, max_results=30, proxies=None):
    """Perform a Startpage (Google-powered) search."""
    print(f"{Fore.CYAN}[INFO] Searching Startpage for '{query}'...{Style.RESET_ALL}")
    base_url = "https://www.startpage.com/sp/search"
    results = []

    with tqdm(total=max_results, desc="Startpage Progress", colour="magenta") as pbar:
        for page in range(1, (max_results // 10) + 2):
            params = {'query': query, 'page': page}
            response = search_engine_request(base_url, params, proxies, "Startpage")
            if not response:
                break
            soup = BeautifulSoup(response.text, "html.parser")
            page_links = [a.get('href') for a in soup.find_all("a") if a.get('href') and 'http' in a.get('href')]
            results.extend(page_links[:max_results - len(results)])
            pbar.update(len(page_links))
            if len(results) >= max_results:
                break
    return results[:max_results]

def load_platforms(file_path):
    """Load platform keywords from a file."""
    try:
        with open(file_path, 'r') as f:
            platforms = [line.strip() for line in f if line.strip()]
            print(f"{Fore.CYAN}[INFO]{Fore.YELLOW} Loaded {Fore.GREEN}{len(platforms)}{Fore.YELLOW} platforms.{Style.RESET_ALL}")
            return platforms
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] File '{file_path}' not found.{Style.RESET_ALL}")
        return []

def detect_platforms(links, platforms):
    """Check for platform presence in search results."""
    detected = {}
    for link in links:
        for platform in platforms:
            if platform.lower() in link.lower():
                detected.setdefault(platform, []).append(link)
    return detected

def main():
    parser = argparse.ArgumentParser(description="Search for a username on multiple search engines.")
    parser.add_argument('username', type=str, help="Username to search for.")
    parser.add_argument('-prox', '--proxy_file', type=str, nargs='?', const="proxies.txt",
                        help="Path to a proxy list file (one per line).")
    parser.add_argument('-n', '--num_results', type=int, default=30, help="Number of search results to fetch (default 30).")
    args = parser.parse_args()

    username = args.username
    proxies_file = args.proxy_file
    num_results = args.num_results

    # Load proxies if specified
    proxies = []
    if proxies_file and os.path.exists(proxies_file):
        with open(proxies_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"{Fore.CYAN}[INFO] Loaded {Fore.GREEN}{len(proxies)}{Fore.YELLOW} proxies.{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Searching {Fore.YELLOW}DuckDuckGo, Bing, and Startpage{Fore.CYAN} for '{Fore.GREEN}{username}{Fore.CYAN}'...\n")

    # Run searches on all three engines
    results = set()
    results.update(duckduckgo_search(username, num_results, proxies))
    results.update(bing_search(username, num_results, proxies))
    results.update(startpage_search(username, num_results, proxies))

    # Deduplicate and limit results, preserving order
    results = list(dict.fromkeys(results))[:num_results]

    if not results:
        print(f"{Fore.RED}[INFO]{Fore.YELLOW} No results found.{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}Search Results:")
    for idx, link in enumerate(results, 1):
        print(f"{Fore.YELLOW}{idx}.{Fore.CYAN} {link}{Style.RESET_ALL}")

    platforms = load_platforms("config/platforms.txt")
    detected = detect_platforms(results, platforms)

    print(f"\n{Fore.CYAN}Detected Social Platforms:")
    if detected:
        for platform, urls in detected.items():
            print(f"{Fore.MAGENTA}{platform}:{Style.RESET_ALL}")
            for url in urls:
                print(f"  - {Fore.GREEN}{url}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[INFO]{Fore.YELLOW} No known platforms detected.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

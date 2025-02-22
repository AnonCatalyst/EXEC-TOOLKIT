import requests
import random
import time
import argparse
import re
import multiprocessing
from tqdm import tqdm
from colorama import Fore, Style, init
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize colorama for colorful output
init(autoreset=True)

# Test URLs for proxy validation
TEST_URL = "http://httpbin.org/ip"
SSL_TEST_URL = "https://www.google.com"

# Initialize UserAgent instance
ua = UserAgent()

# Load proxy sources from file
def load_proxy_sources(file_path="config/proxy_sources.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        tqdm.write(f"{Fore.RED}[✘] Error loading proxy sources: {e}{Style.RESET_ALL}")
        return []

# Random delay to mimic human behavior (between 2 to 5 seconds)
def random_delay():
    delay = random.uniform(2, 5)
    time.sleep(delay)

# Scrape proxies from a given URL
def scrape_proxies(url, check=False):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers, timeout=10)
        proxies = set(re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', response.text))
        if proxies:
            tqdm.write(f"{Fore.WHITE}[✔] {Fore.GREEN}{len(proxies)}{Fore.WHITE} proxies scraped from {Fore.CYAN}{url}{Style.RESET_ALL}")
        # Do not output message if no proxies found
        return proxies
    except requests.exceptions.RequestException:
        #tqdm.write(f"{Fore.RED}[✘] Failed to scrape {Fore.CYAN}{url}{Style.RESET_ALL}")
        return set()

# Validate a proxy for HTTP status, SSL support, and anonymity
def validate_proxy(proxy):
    proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    try:
        response = requests.get(TEST_URL, proxies=proxies, timeout=5)
        if response.status_code != 200:
            return None
        try:
            requests.get(SSL_TEST_URL, proxies=proxies, timeout=5)
            ssl_support = True
        except requests.exceptions.RequestException:
            ssl_support = False

        anonymity = "Transparent"
        if "X-Forwarded-For" not in response.headers and "Via" not in response.headers:
            anonymity = "Elite"
        elif "X-Forwarded-For" in response.headers:
            anonymity = "Anonymous"

        return proxy, ssl_support, anonymity
    except requests.exceptions.RequestException:
        return None

# Process proxies in parallel using multi-processing for validation
def process_proxies(proxies):
    validated_proxies = []
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = list(tqdm(pool.imap(validate_proxy, proxies),
                            total=len(proxies),
                            desc=f"{Fore.CYAN}Validating Proxies{Style.RESET_ALL}",
                            dynamic_ncols=True))
    for result in results:
        if result:
            validated_proxies.append(result)
    return validated_proxies

# Load proxies from a user file
def load_user_proxies(file_path):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        tqdm.write(f"{Fore.RED}[✘] Error loading proxies from file: {e}{Style.RESET_ALL}")
        return []

# Main function
def main():
    parser = argparse.ArgumentParser(description="ProxySponge - Scrape & Validate Proxies")
    parser.add_argument("-p", "--proxies", help="Validate proxies from a custom file")
    parser.add_argument("-c", "--check", action="store_true", help="Enable validation after scraping")
    args = parser.parse_args()

    # Either load from a user file...
    if args.proxies:
        tqdm.write(f"{Fore.YELLOW}[📂] Loading user proxies from {args.proxies}{Style.RESET_ALL}")
        proxies = set(load_user_proxies(args.proxies))
    # ...or scrape from the configured sources concurrently.
    else:
        proxy_sources = load_proxy_sources()
        proxies = set()
        if proxy_sources:
            tqdm.write(f"{Fore.MAGENTA}[ℹ] Scraping proxies from {len(proxy_sources)} sources concurrently...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=min(len(proxy_sources), 10)) as executor:
                future_to_source = {executor.submit(scrape_proxies, source, args.check): source for source in proxy_sources}
                for future in tqdm(as_completed(future_to_source), total=len(proxy_sources),
                                   desc=f"{Fore.MAGENTA}Scraping Sources{Style.RESET_ALL}",
                                   dynamic_ncols=True, leave=False):
                    result = future.result()
                    proxies.update(result)
        else:
            tqdm.write(f"{Fore.RED}[✘] No proxy sources found in configuration.{Style.RESET_ALL}")
            return

    if not proxies:
        tqdm.write(f"{Fore.RED}[✘] No proxies found. Exiting.{Style.RESET_ALL}")
        return

    # Validate proxies if the --check flag is enabled
    if args.check:
        tqdm.write(f"{Fore.YELLOW}[🔄] Validating all proxies...{Style.RESET_ALL}")
        validated_proxies = process_proxies(proxies)
    else:
        validated_proxies = list(proxies)

    # Save the results to a file
    with open("validated_proxies.txt", "w") as f:
        for entry in validated_proxies:
            if isinstance(entry, tuple):
                f.write(f"{entry[0]} | SSL: {entry[1]} | Anonymity: {entry[2]}\n")
            else:
                f.write(f"{entry}\n")

    # Prepare and print a one-line colorful summary
    if args.check:
        total = len(validated_proxies)
        ssl_count = sum(1 for proxy in validated_proxies if proxy[1])
        elite_count = sum(1 for proxy in validated_proxies if proxy[2] == 'Elite')
        anon_count = sum(1 for proxy in validated_proxies if proxy[2] == 'Anonymous')
        summary = (f"{Fore.CYAN}[📊] Summary: {Fore.GREEN}Total: {total}  "
                   f"{Fore.YELLOW}| SSL: {ssl_count}  {Fore.BLUE}| Elite: {elite_count}  "
                   f"{Fore.MAGENTA}| Anonymous: {anon_count}{Style.RESET_ALL}")
    else:
        summary = f"{Fore.CYAN}[📊] Total proxies scraped: {Fore.GREEN}{len(validated_proxies)}{Style.RESET_ALL}"
    print("=" * 60)
    print(summary)
    print("=" * 60)

if __name__ == "__main__":
    main()

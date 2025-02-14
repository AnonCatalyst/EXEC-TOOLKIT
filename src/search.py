import os
import time
import random
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
from urllib.parse import urlparse

init(autoreset=True)
ua = UserAgent()

def human_delay():
    time.sleep(random.uniform(1, 3))

def load_platform_keywords():
    platforms = set()
    if os.path.exists("config/platforms.txt"):
        with open("config/platforms.txt", "r") as f:
            platforms = set(f.read().split())
    return platforms

def fetch_results(query, num_results, source="duckduckgo", country=None, language=None, date_range=None):
    try:
        if source == "duckduckgo":
            return fetch_duckduckgo_results(query, num_results, country, language, date_range)
        elif source == "google":
            return fetch_google_results(query, num_results, country, language, date_range)
        else:
            raise ValueError("Unsupported source provided")
    except Exception as e:
        print(Fore.RED + f"Error fetching results from {source}: {e}")
        return []

def fetch_duckduckgo_results(query, num_results, country=None, language=None, date_range=None):
    results = set()
    duckduckgo_pages = num_results // 10 if num_results >= 10 else 1
    for page in range(duckduckgo_pages):
        url = f"https://duckduckgo.com/html/?q={query}&s={page * 10}"
        if country:
            url += f"&kp={country}"
        if language:
            url += f"&lang={language}"
        if date_range:
            url += f"&df={date_range}"
        
        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", class_="result__url")
        for link in links:
            href = link.get("href")
            if href and href.startswith(('http://', 'https://')):
                results.add(href)
        human_delay()
        print(Fore.GREEN + f"Fetched DuckDuckGo page {page + 1}/{duckduckgo_pages}.")
    return list(results)

def fetch_google_results(query, num_results, country=None, language=None, date_range=None):
    google_results = set()
    search_parameters = []
    if country:
        search_parameters.append(f"gl={country}")
    if language:
        search_parameters.append(f"hl={language}")
    if date_range:
        search_parameters.append(f"tbs=qdr:{date_range}")
    full_query = f"{query} {' '.join(search_parameters)}"
    
    for result in google_search(full_query, num_results=num_results):
        google_results.add(result)
    return list(google_results)

def search_with_threading(query, num_results=30, country=None, language=None, date_range=None):
    all_results = set()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_results, query, num_results, source="duckduckgo",
                            country=country, language=language, date_range=date_range): "duckduckgo",
            executor.submit(fetch_results, query, num_results, source="google",
                            country=country, language=language, date_range=date_range): "google"
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                results = future.result()
                all_results.update(results)
                print(Fore.GREEN + f"{source.capitalize()} results fetched.")
            except Exception as e:
                print(Fore.RED + f"Error fetching {source} results: {e}")
    
    print(Fore.GREEN + f"\nTotal Results: {len(all_results)}")
    return list(all_results)[:num_results]

def display_analysis(analysis):
    if not analysis:
        print(Fore.RED + "No results found.")
        return

    platforms = load_platform_keywords()
    social_platforms = []

    for idx, url in enumerate(analysis, start=1):
        try:
            response = requests.get(url, headers={"User-Agent": ua.random}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "No Title"
            description_meta = soup.find('meta', attrs={'name': 'description'}) or \
                               soup.find('meta', attrs={'property': 'og:description'})
            description = description_meta.get('content', 'No Description').strip() if description_meta else "No Description"
            
            print(Fore.CYAN + f"\n🔍 Result {idx}")
            print(Fore.GREEN + f"🌍 URL: {url}")
            print(Fore.YELLOW + f"📖 Title: {title}")
            print(Fore.YELLOW + f"📖 Description: {description}")
            print(Fore.CYAN + "─" * 50)
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"🚨 Error fetching {url}: {e}")

def run_search():
    query_file = "config/query.txt"
    results_file = "config/num_results.txt"
    country_file = "config/country.txt"
    language_file = "config/language.txt"
    date_range_file = "config/date_range.txt"

    # Load or prompt for query
    if os.path.exists(query_file):
        with open(query_file, "r") as file:
            query = file.read().strip()
    else:
        query = input(Fore.GREEN + "Enter search query: ")
        with open(query_file, "w") as file:
            file.write(query)
        print(Fore.YELLOW + f"New query saved to {query_file}.")

    # Load or prompt for number of results
    if os.path.exists(results_file):
        with open(results_file, "r") as file:
            num_results = int(file.read().strip())
    else:
        num_results = int(input(Fore.GREEN + "Enter number of results: "))
        with open(results_file, "w") as file:
            file.write(str(num_results))
        print(Fore.YELLOW + f"Number of results saved to {results_file}.")

    # Load or prompt for country code
    if os.path.exists(country_file):
        with open(country_file, "r") as file:
            country = file.read().strip()
    else:
        country = input(Fore.GREEN + "Enter country code (or press Enter to skip): ").strip()
        with open(country_file, "w") as file:
            file.write(country)
        print(Fore.YELLOW + f"Country code saved to {country_file}.")

    # Load or prompt for language code
    if os.path.exists(language_file):
        with open(language_file, "r") as file:
            language = file.read().strip()
    else:
        language = input(Fore.GREEN + "Enter language code (or press Enter to skip): ").strip()
        with open(language_file, "w") as file:
            file.write(language)
        print(Fore.YELLOW + f"Language code saved to {language_file}.")

    # Load or prompt for date range
    if os.path.exists(date_range_file):
        with open(date_range_file, "r") as file:
            date_range = file.read().strip()
    else:
        date_range = input(Fore.GREEN + "Enter date range (e.g., d1 for last 24 hours, or press Enter to skip): ").strip()
        with open(date_range_file, "w") as file:
            file.write(date_range)
        print(Fore.YELLOW + f"Date range saved to {date_range_file}.")

    results = search_with_threading(query, num_results=num_results, country=country, language=language, date_range=date_range)
    display_analysis(results)

    time.sleep(1)

if __name__ == "__main__":
    run_search()

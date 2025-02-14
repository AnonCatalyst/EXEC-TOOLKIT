import requests
import random
import time
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore
from bs4 import BeautifulSoup
import socket

print(Fore.MAGENTA + "\n-------------------------------------")
print(Fore.GREEN + "Domain Query Enrichment\n")

# Initialize colorama and UserAgent
try:
    init(strip=False)
except ImportError:
    Fore = type('FakeFore', (object,), {})
ua = UserAgent()

# Set headers
headers = {"User-Agent": ua.random}

# Initialize counters for valid results and errors
valid_count = 0
error_count = 0

# Function to delay between requests with jitter
def human_delay():
    time.sleep(random.uniform(0.5, 2))

# Function to extract OSINT metadata from the domain
def extract_metadata(response, query):
    metadata = {}
    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("title")
    description_tag = soup.find("meta", attrs={"name": "description"}) or \
                      soup.find("meta", attrs={"property": "og:description"})
    
    # Extract data safely
    if title_tag and title_tag.string:
        metadata["title"] = title_tag.string.strip()
    if description_tag and description_tag.get("content"):
        metadata["description"] = description_tag.get("content").strip()
    
    # Extract headers
    headers_keys = ["Server", "X-Powered-By", "Content-Type", "Last-Modified", 
                    "Content-Length", "X-Frame-Options", "Strict-Transport-Security", 
                    "X-Content-Type-Options"]
    for key in headers_keys:
        if key in response.headers:
            metadata[key.lower()] = response.headers.get(key)
    
    # Extract IP and ASN info
    try:
        ip_address = socket.gethostbyname(response.url.split("/")[2])
        metadata["ip_address"] = ip_address
        ip_info = requests.get(f"https://ipwhois.app/json/{ip_address}").json()
        metadata.update({"asn": ip_info.get("asn"), "org": ip_info.get("org")})
    except Exception:
        metadata.update({"ip_address": "Could not fetch IP", 
                         "asn": "Could not fetch ASN", 
                         "org": "Could not fetch organization"})

    # Query detection
    metadata["query_found_in_title"] = query.lower() in metadata.get("title", "").lower()
    metadata["query_found_in_description"] = query.lower() in metadata.get("description", "").lower()
    return metadata

# Function to fetch URL and handle errors
def fetch_url(query, domain):
    global valid_count, error_count
    url = f"http://{query}.{domain}"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # Check if request was successful
        metadata = extract_metadata(response, query)
        print(f"{Fore.GREEN}✔️ Successfully retrieved data from {url}{Fore.RESET}")
        
        # Increment valid count
        valid_count += 1

        # Display available metadata
        for key in ["title", "description", "server", "x_powered_by", "content_type", 
                    "last_modified", "content_length", "x_frame_options", 
                    "strict_transport_security", "x_content_type_options", "ip_address", "asn", "org"]:
            if key in metadata:
                print(f"{Fore.CYAN}{key.capitalize()}: {metadata[key]}{Fore.RESET}")
        
        # Highlight query presence in title or description
        if metadata.get("query_found_in_title"):
            print(f"{Fore.MAGENTA}Query '{query}' found in the title!{Fore.RESET}")
        if metadata.get("query_found_in_description"):
            print(f"{Fore.MAGENTA}Query '{query}' found in the description!{Fore.RESET}")

        # Red line divider
        print(f"{Fore.RED}{'-' * 50}{Fore.RESET}")
        
        return {"url": url, "metadata": metadata}
    except requests.exceptions.RequestException:
        # Increment error count
        error_count += 1
        return None
    finally:
        human_delay()

# Main function
def main():
    global valid_count, error_count
    with open("config/domains.txt", "r") as file:
        domains = set(file.read().split(","))  # Use set to remove duplicates
    with open("config/query.txt", "r") as file:
        query = file.read().strip()
    
    print(f"{Fore.CYAN}📊 Total unique domains to test: {len(domains)}{Fore.RESET}")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_url, query, domain.strip()) for domain in domains]
        for future in as_completed(futures):
            future.result()

    # Display status table
    print(Fore.YELLOW + "\nStatus Table")
    print(Fore.GREEN + "-----------------------------")
    print(f"Valid Responses: {valid_count}")
    print(f"Errors: {error_count}")
    print(Fore.RESET + "-----------------------------")

if __name__ == "__main__":
    main()

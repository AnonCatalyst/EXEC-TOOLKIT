import time
import random
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init(autoreset=True)

# Colors for the animated color effect
COLORS = [
    "\033[32m",  # Green
    "\033[31m",  # Red
    "\033[33m",  # Yellow
    "\033[34m",  # Blue
    "\033[35m",  # Magenta
    "\033[36m",  # Cyan
]

# Function to simulate checking URLs with animated progress
def generate_and_check_urls(username, platforms):
    # Use defaultdict to handle unknown error statuses gracefully
    error_counts = defaultdict(int)
    valid_urls = []
    detection_list = []  # List to store URLs with detected queries in title/description

    # Create a list of URLs to check
    urls_to_check = [(f"{platform}{username}", username) for platform in platforms]

    # Use ThreadPoolExecutor for concurrent checking
    with ThreadPoolExecutor() as executor:
        for result in executor.map(check_url, urls_to_check):
            url, status, detections = result

            # Print live results as soon as each URL is checked
            if status == "OK":
                valid_urls.append(url)
                if detections:
                    detection_list.extend(detections)
                print(f"{Fore.MAGENTA}◈ {Fore.CYAN}SOCIAL OWL{Fore.MAGENTA}〘{Fore.GREEN}✔{Fore.MAGENTA}〙{Fore.RESET}Found Social{Fore.RED}︰{Fore.BLUE} {url} {Fore.RED}⌯{Fore.GREEN} OK{Fore.RESET}")   # Green for valid URLs
            else:
                error_counts[status] += 1

    return valid_urls, error_counts, detection_list

# Function to handle URL checking
def check_url(url_info):
    url, username = url_info
    detection_list = []

    try:
        # Make the actual HTTP request to check the URL
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            # Parse the title and description from the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ''
            description = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            description = description['content'] if description else ''

            # Check if the username is found in the title or description
            if (title and username.lower() in title.lower()) or (description and username.lower() in description.lower()):
                detection_list.append(url)

            return url, "OK", detection_list
        else:
            return url, str(response.status_code), detection_list

    except requests.exceptions.RequestException:
        # Handle any errors like timeouts
        return url, "Invalid", detection_list

# Function to load platforms from the file
def load_platforms(filename):
    try:
        with open(filename, 'r') as file:
            platforms = [line.strip() for line in file.readlines()]
        print(f"Total URLs loaded for scanning: {len(platforms)}")
        return platforms
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found!")
        return []

# Function to display error summary table
def display_error_summary(error_counts):
    print("\nError Summary:")
    print(f"{'Error Type':<15} | {'Count'}")
    print("-" * 30)
    for error_type, count in error_counts.items():
        print(f"{error_type:<15} | {count}")

# Function to simulate an animated banner with hacker theme
def animated_banner():
    banner_text = "SOCIAL OWL"
    # Setting background color to black and text color to green
    for i in range(len(banner_text)):
        color = random.choice(COLORS)  # Cycle through colors for each letter
        print(f"{color}{banner_text[i]}", end='', flush=True)
        time.sleep(0.1)  # Simulate typing effect
    print("\n\033[32m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")  # Green line
    time.sleep(0.5)

# Function to animate the border
def animated_border():
    border_chars = ["|", "-", "/", "\\", "|", "-", "/", "\\"]
    for i in range(20):  # Length of the border
        color = random.choice(COLORS)  # Randomly pick a color for the border
        print(f"{color}{border_chars[i % len(border_chars)]}{Fore.RESET}", end="", flush=True)
        time.sleep(0.1)  # Simulate border animation effect
    print("\n", end="")

# Main function
def main():
    # Argument parsing for username and file path
    parser = argparse.ArgumentParser(
        description="This script checks social media accounts for a given username across multiple platforms."
    )

    # Add argument for username
    parser.add_argument(
        "username",
        help="The username to search for across social media platforms."
    )

    # Add argument for platforms file with default value
    parser.add_argument(
        "-f", "--file",
        default="config/social.txt",  # Default file is 'social.txt'
        help="The path to the file containing the list of social media platforms (default: 'social.txt')."
    )

    # Parse the arguments
    args = parser.parse_args()

    # Show help if requested
    if args.username == 'help' or args.username == '--help' or args.username == '-h':
        help_menu.show_help()
        return

    # Display colorful hacker-themed border
    print("\033[32m▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁")  # Green line
    animated_border()

    # Display animated banner with hacker theme
    animated_banner()

    # Display another animated border
    animated_border()

    # Load platforms from the provided file path or default file
    platforms = load_platforms(args.file)
    if not platforms:
        return  # Exit if no platforms were loaded

    # Use the username from the command-line argument
    username = args.username

    # Generate and check URLs
    print("\nGenerating and checking URLs...")
    valid_urls, error_counts, detection_list = generate_and_check_urls(username, platforms)

    # Detection list (with username/query in title or description)
    if detection_list:
        print("\nDetected Social Media Accounts (Username found in title or description):")
        for url in detection_list:
            print(f"{Fore.GREEN}🔍 {Fore.MAGENTA}{url} {Fore.YELLOW}- {Fore.GREEN}OK{Fore.RESET}")  # Adding color to detection list URLs and status

    # Display error summary without showing error URLs
    display_error_summary(error_counts)

if __name__ == "__main__":
    main()

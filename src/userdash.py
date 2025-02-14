import time
import instaloader
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from colorama import Fore, init
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import sys
from datetime import datetime

init(autoreset=True)
ua = UserAgent()
L = instaloader.Instaloader()

def load_username_from_file():
    try:
        with open('config/query.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Error: 'query.txt' file not found!")
        return None

def fetch_instagram_data(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        data = {
            'Platform': 'Instagram',
            'Username': profile.username,
            'Followers': profile.followers,
            'Following': profile.followees,
            'Posts': profile.mediacount,
            'Biography': profile.biography,
            'Profile Picture': profile.profile_pic_url,
            'Profile URL': f'https://www.instagram.com/{username}/'  # Manually adding the profile URL
        }
        sys.stdout.write(f"\r{Fore.GREEN}Instagram data retrieval completed for {username}. ")
        sys.stdout.flush()
        return data
    except Exception:
        sys.stdout.write(f"\r{Fore.RED}Instagram data retrieval failed for {username}. ")
        sys.stdout.flush()
        return None

def fetch_reddit_data(username):
    try:
        url = f'https://www.reddit.com/user/{username}/about.json'
        response = requests.get(url, headers={'User-Agent': ua.random}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = {
                'Platform': 'Reddit',
                'Username': data['data']['name'],
                'Karma': data['data'].get('link_karma', 0) + data['data'].get('comment_karma', 0),
                'Link Karma': data['data'].get('link_karma', 0),
                'Comment Karma': data['data'].get('comment_karma', 0),
                'Profile URL': f'https://www.reddit.com/user/{username}/'  # Manually adding the profile URL
            }
            sys.stdout.write(f"\r{Fore.GREEN}Reddit data retrieval completed for {username}. ")
            sys.stdout.flush()
            return result
        return None
    except requests.RequestException:
        sys.stdout.write(f"\r{Fore.RED}Reddit data retrieval failed for {username}. ")
        sys.stdout.flush()
        return None

def fetch_github_data(username):
    try:
        url = f'https://api.github.com/users/{username}'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = {
                'Platform': 'GitHub',
                'Username': data.get('login'),
                'Public Repositories': data.get('public_repos'),
                'Followers': data.get('followers'),
                'Following': data.get('following'),
                'Bio': data.get('bio'),
                'Profile URL': f'https://github.com/{username}'  # Manually adding the profile URL
            }
            sys.stdout.write(f"\r{Fore.GREEN}GitHub data retrieval completed for {username}. ")
            sys.stdout.flush()
            return result
        return None
    except requests.RequestException:
        sys.stdout.write(f"\r{Fore.RED}GitHub data retrieval failed for {username}. ")
        sys.stdout.flush()
        return None

def extract_meta_data(url):
    try:
        response = requests.get(url, headers={'User-Agent': ua.random}, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_data = {tag.get('property'): tag.get('content') for tag in soup.find_all('meta') if tag.get('property')}
            
            # Extract additional useful metadata
            meta_data['Title'] = soup.title.string if soup.title else "No Title Available"
            meta_data['Description'] = meta_data.get('og:description', 'No Description Available')
            meta_data['Image'] = meta_data.get('og:image', 'No Image Available')
            meta_data['URL'] = url
            meta_data['Site Name'] = meta_data.get('og:site_name', 'No Site Name Available')
            meta_data['Type'] = meta_data.get('og:type', 'No Type Available')
            meta_data['Locale'] = meta_data.get('og:locale', 'No Locale Available')

            return {k: v for k, v in meta_data.items() if v not in [None, '', 'No Description Available', 'No Title Available', 'No Image Available']}
        return None
    except requests.RequestException:
        return None

def check_platforms_availability(username):
    visited_urls = set()
    meta_results = []
    try:
        with open('config/platforms.txt', 'r') as file:
            platforms = [platform.strip() for platform in file.readlines()]
        for platform_url in platforms:
            full_url = f'{platform_url}/{username}'
            if full_url not in visited_urls:
                visited_urls.add(full_url)
                meta_data = extract_meta_data(full_url)
                if meta_data:
                    meta_results.append(meta_data)
    except Exception:
        pass
    return meta_results

def print_platform_data(platform_name, platform_data):
    if platform_data:
        print(f"{Fore.MAGENTA}Profile Data:{Fore.YELLOW}\n{'='*40}")
        for key, value in platform_data.items():
            if value:  # Only display values that are not None or empty
                print(f"{Fore.CYAN}{key.capitalize()}:{Fore.WHITE} {value}")
        print(f"{Fore.CYAN}{platform_name} Profile URL:{Fore.BLUE} {platform_data.get('Profile URL', 'No URL Available')}")
        print(f"{'-'*40}")
    else:
        sys.stdout.write(f"\r{Fore.RED}No data available for {platform_name}.{' ' * 10}")
        sys.stdout.flush()

def print_additional_platform_data(platform_data):
    """Function to handle additional platform metadata with time and date."""
    if platform_data:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{Fore.YELLOW}Metadata retrieved on {current_time}:\n{'='*40}")
        for key, value in platform_data.items():
            if value:  # Only display values that are not None or empty
                print(f"{Fore.CYAN}{key.capitalize()}:{Fore.WHITE} {value}")
        print(f"{'-'*40}")
    else:
        sys.stdout.write(f"\r{Fore.RED}No metadata found.{' ' * 10}")
        sys.stdout.flush()

def fetch_data_for_user(username):
    if not username:
        print(f"{Fore.RED}❌ No username provided.")
        return
    
    print(f"\n{Fore.CYAN}🔍 Retrieving data for {username}...\n{'-'*40}")
    
    profile_url_shown = set()  # Use a set to keep track of the profile URLs shown
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            'Instagram': executor.submit(fetch_instagram_data, username),
            'Reddit': executor.submit(fetch_reddit_data, username),
            'GitHub': executor.submit(fetch_github_data, username),
            'Platforms': executor.submit(check_platforms_availability, username)
        }

        # Live results with dynamic printing
        instagram_result = futures['Instagram'].result()
        if instagram_result:
            print_platform_data("Instagram", instagram_result)
            if instagram_result.get('Profile URL') not in profile_url_shown:
                print(f"{Fore.CYAN}Instagram Profile URL:{Fore.BLUE} {instagram_result.get('Profile URL', 'No URL Available')}")
                profile_url_shown.add(instagram_result.get('Profile URL'))
            time.sleep(1)  # Short delay between platform results
        
        reddit_result = futures['Reddit'].result()
        if reddit_result:
            print_platform_data("Reddit", reddit_result)
            if reddit_result.get('Profile URL') not in profile_url_shown:
                print(f"{Fore.CYAN}Reddit Profile URL:{Fore.BLUE} {reddit_result.get('Profile URL', 'No URL Available')}")
                profile_url_shown.add(reddit_result.get('Profile URL'))
            time.sleep(1)  # Short delay between platform results
        
        github_result = futures['GitHub'].result()
        if github_result:
            print_platform_data("GitHub", github_result)
            if github_result.get('Profile URL') not in profile_url_shown:
                print(f"{Fore.CYAN}GitHub Profile URL:{Fore.BLUE} {github_result.get('Profile URL', 'No URL Available')}")
                profile_url_shown.add(github_result.get('Profile URL'))
            time.sleep(1)  # Short delay between platform results
        
        platforms_result = futures['Platforms'].result()
        if platforms_result:
            for platform_meta in platforms_result:
                print_additional_platform_data(platform_meta)
                time.sleep(1)  # Short delay between platform results

def main():
    username = load_username_from_file()
    fetch_data_for_user(username)

if __name__ == "__main__":
    main()

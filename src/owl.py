import time
import random
import requests
import re
import os
from bs4 import BeautifulSoup
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import argparse
from fpdf import FPDF

# Initialize colorama
init(autoreset=True)

# Colors for console output
COLORS = [
    "\033[32m",  # Green
    "\033[31m",  # Red
    "\033[33m",  # Yellow
    "\033[34m",  # Blue
    "\033[35m",  # Magenta
    "\033[36m",  # Cyan
]

GREY = Fore.LIGHTBLACK_EX

result_pool = []
PDF_OPTION = False  # Global flag to indicate if PDF saving is enabled

def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', 'ignore').decode('latin-1')

# Subclass FPDF to enforce dark-mode styling on every page
class DarkModePDF(FPDF):
    def __init__(self, username, total_scanned):
        super().__init__()
        self.username = username
        self.total_scanned = total_scanned
        self.add_page()  # Ensure a page is open

    def header(self):
        # Dark-mode header: fill background and add header text
        self.set_fill_color(0, 0, 0)
        self.rect(0, 0, self.w, self.h, 'F')
        lime_green = (50,205,50)
        white = (255,255,255)
        grey_color = (128,128,128)
        self.set_text_color(*lime_green)
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, clean_text("SOCIAL OWL Investigation Report"), ln=True, align="C")
        self.set_text_color(*white)
        self.set_font("Arial", '', 12)
        self.cell(0, 10, clean_text(f"Username: {self.username}"), ln=True)
        self.cell(0, 10, clean_text(f"URLs Checked: {len(result_pool)}"), ln=True)
        self.ln(5)
        self.set_line_width(0.5)
        self.set_draw_color(*grey_color)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)

    def footer(self):
        # Footer with page number in dark grey
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.set_text_color(169,169,169)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, 'C')

def extract_profile_details(soup, username):
    details = {}
    # Extract HTML bio elements (consolidated into one field)
    bio_elements = soup.find_all(attrs={"class": re.compile("bio|about|profile", re.I)}) + \
                   soup.find_all(attrs={"id": re.compile("bio|about|profile", re.I)})
    if bio_elements:
        html_bio = " | ".join([el.get_text(separator=" ", strip=True) for el in bio_elements])
        details["html_bio"] = html_bio
    # Extract external links (only include links that start with "https://")
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not href.startswith("https://"):
            continue
        # Case-insensitive check: convert both sides to lowercase
        if username.lower() in a.get_text().lower() or (username.lower() in href.lower()):
            links.append(href)
    if links:
        details["links"] = list(set(links))
    page_text = soup.get_text()
    metrics = {
        "followers": r'([\d,]+)\s+Followers',
        "following": r'([\d,]+)\s+Following',
        "posts": r'([\d,]+)\s+Posts',
        "location": r'Location[:\s]+([A-Za-z0-9,.\s]+)',
        "joined": r'Joined\s+([A-Za-z]+\s+\d{4})'
    }
    for key, pattern in metrics.items():
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()
    profile_image_tag = soup.find('meta', attrs={'property': 'og:image'})
    if profile_image_tag and 'content' in profile_image_tag.attrs:
        details["profile_image"] = profile_image_tag['content']
    og_title_tag = soup.find('meta', attrs={'property': 'og:title'})
    if og_title_tag and 'content' in og_title_tag.attrs:
         details["og_title"] = og_title_tag['content'].strip()
    canonical_tag = soup.find('link', rel='canonical')
    if canonical_tag and 'href' in canonical_tag.attrs:
         details["canonical_url"] = canonical_tag['href'].strip()
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    if keywords_tag and 'content' in keywords_tag.attrs:
         details["meta_keywords"] = keywords_tag['content'].strip()
    h1_tags = soup.find_all('h1')
    if h1_tags:
         details["h1_text"] = " | ".join([h1.get_text(separator=" ", strip=True) for h1 in h1_tags])
    h2_tags = soup.find_all('h2')
    if h2_tags:
         details["h2_text"] = " | ".join([h2.get_text(separator=" ", strip=True) for h2 in h2_tags])
    return details

def crawl_additional_data(url, username):
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.content.decode('utf-8', 'ignore'), 'html.parser')
            additional_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith("https://"):
                    additional_links.append(href)
            return {"additional_links": list(set(additional_links))}
        return {}
    except Exception as e:
        return {}

def check_url(url_info):
    url, username = url_info
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.content.decode('utf-8', 'ignore'), 'html.parser')
            title = soup.title.string if soup.title else ''
            desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            description = desc_tag['content'] if desc_tag and 'content' in desc_tag.attrs else ''
            if title.strip() == description.strip():
                description = ""
            page_text = soup.get_text()
            # Case-insensitive regex matches
            title_occurrences = len(re.findall(r'\b' + re.escape(username) + r'\b', title, re.IGNORECASE))
            description_occurrences = len(re.findall(r'\b' + re.escape(username) + r'\b', description, re.IGNORECASE))
            text_mentions = len(re.findall(rf'[@#]{re.escape(username)}', page_text, re.IGNORECASE))
            html_mentions = len(re.findall(rf'[@#]{re.escape(username)}', str(soup), re.IGNORECASE))
            mention_occurrences = text_mentions + html_mentions
            total_occurrences = title_occurrences + description_occurrences + mention_occurrences
            if total_occurrences <= 2:
                return url, "OK", []
            detection_methods = []
            if title_occurrences:
                detection_methods.append("Title")
            if description_occurrences:
                detection_methods.append("Description")
            if mention_occurrences:
                detection_methods.append("Mentions/Tags")
            detection = {
                "url": url,
                "title_occurrences": title_occurrences,
                "description_occurrences": description_occurrences,
                "mention_occurrences": mention_occurrences,
                "detection_methods": detection_methods,
                "page_title": title,
                "page_description": description,
                "profile_details": extract_profile_details(soup, username)
            }
            additional_data = crawl_additional_data(url, username)
            detection["profile_details"].update(additional_data)
            return url, "OK", [detection]
        return url, str(response.status_code), []
    except Exception as e:
        return url, "Error", []

def generate_and_check_urls(username, platforms):
    error_counts = defaultdict(int)
    detection_list = []
    processed_urls = set()
    urls_to_check = [(f"{platform}{username}", username) for platform in platforms]
    with ThreadPoolExecutor() as executor:
        for result in executor.map(check_url, urls_to_check):
            url, status, detections = result
            result_pool.append({"url": url, "status": status, "detections": detections})
            if status == "OK" and detections:
                for detection in detections:
                    if detection["url"] not in processed_urls:
                        detection_list.append(detection)
                        processed_urls.add(detection["url"])
                        print_detection_details(detection)
            elif status == "OK":
                print(f"{Fore.MAGENTA}◈ {Fore.CYAN}SOCIAL OWL{Fore.MAGENTA}〘{Fore.GREEN}✔{Fore.MAGENTA}〙{Fore.RESET}Found Social: {Fore.BLUE}{url}{Fore.RED} ⌯ {Fore.GREEN}OK{Fore.RESET}")
            else:
                error_counts[status] += 1
    return error_counts, detection_list

def print_detection_details(detection):
    print(f"{Fore.MAGENTA}◈ {Fore.CYAN}SOCIAL OWL{Fore.MAGENTA}〘{Fore.GREEN}✔{Fore.MAGENTA}〙{Fore.RESET}Found Social: {Fore.BLUE}{detection['url']}{Fore.RESET}")
    print(f"{GREY}    {Fore.CYAN}Detected via:{Style.RESET_ALL} {', '.join(detection['detection_methods'])}")
    if detection['title_occurrences'] > 0:
         print(f"{GREY}    {Fore.CYAN}Title Occurrences:{Style.RESET_ALL} {detection['title_occurrences']}")
    if detection['description_occurrences'] > 0:
         print(f"{GREY}    {Fore.CYAN}Description Occurrences:{Style.RESET_ALL} {detection['description_occurrences']}")
    if detection['mention_occurrences'] > 0:
         print(f"{GREY}    {Fore.CYAN}Mentions/Tags Occurrences:{Style.RESET_ALL} {detection['mention_occurrences']}")
    if detection.get("page_title"):
         print(f"{GREY}    {Fore.CYAN}Page Title:{Style.RESET_ALL} {detection['page_title'][:100]}")
    if detection.get("page_description"):
         print(f"{GREY}    {Fore.CYAN}Page Description:{Style.RESET_ALL} {detection['page_description'][:100]}")
    profile = detection.get("profile_details", {})
    for key, value in profile.items():
         value_str = str(value)
         if key in ["followers", "following"]:
             print(f"{GREY}    {Fore.CYAN}{key.title()}:{Style.RESET_ALL} {value_str}")
         else:
             if len(value_str) > 300:
                 value_str = value_str[:300] + "..."
             print(f"{GREY}    {Fore.CYAN}{key.title()}:{Style.RESET_ALL} {value_str}")
    if PDF_OPTION:
        print(f"{GREY}    Full details are available in the PDF report.")
    print(f"{GREY}{'-'*80}{Style.RESET_ALL}")

def load_platforms(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return []

def generate_pdf_report(username, detection_list, error_counts, total_scanned):
    pdf = DarkModePDF(username, total_scanned)
    lime_green = (50,205,50)
    white = (255,255,255)
    grey_color = (128,128,128)
    dark_green = (0,100,0)
    pdf.ln(5)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(*grey_color)
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*lime_green)
    pdf.cell(0, 10, clean_text("Detected Accounts:"), ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", '', 12)
    for detection in detection_list:
        pdf.set_text_color(*lime_green)
        pdf.cell(0, 10, clean_text(detection['url']), ln=True)
        pdf.set_text_color(*white)
        pdf.cell(40, 10, clean_text("Detection Methods:"), ln=0)
        pdf.multi_cell(0, 10, clean_text(', '.join(detection['detection_methods'])))
        pdf.cell(40, 10, clean_text("Page Title:"), ln=0)
        pdf.multi_cell(0, 10, clean_text(detection.get("page_title", "")))
        pdf.cell(40, 10, clean_text("Page Description:"), ln=0)
        pdf.multi_cell(0, 10, clean_text(detection.get("page_description", "")))
        if detection['title_occurrences'] > 0:
            pdf.cell(40, 10, clean_text(f"Title Occurrences: {detection['title_occurrences']}"), ln=True)
        if detection['description_occurrences'] > 0:
            pdf.cell(40, 10, clean_text(f"Description Occurrences: {detection['description_occurrences']}"), ln=True)
        if detection['mention_occurrences'] > 0:
            pdf.cell(40, 10, clean_text(f"Mentions/Tags Occurrences: {detection['mention_occurrences']}"), ln=True)
        for field in ["html_bio", "links", "followers", "following", "posts", 
                      "location", "joined", "profile_image", "additional_links",
                      "og_title", "canonical_url", "meta_keywords", "h1_text", "h2_text"]:
            if field in detection["profile_details"]:
                pdf.cell(40, 10, clean_text(f"{field.replace('_', ' ').title()}:"),
                         ln=0)
                pdf.multi_cell(0, 10, clean_text(str(detection["profile_details"][field])))
        pdf.ln(3)
        pdf.set_line_width(0.3)
        pdf.set_draw_color(*grey_color)
        current_y = pdf.get_y()
        pdf.line(10, current_y, pdf.w - 10, current_y)
        pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*dark_green)
    pdf.cell(0, 10, clean_text("Error Summary:"), ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*white)
    for error, count in error_counts.items():
        pdf.cell(0, 10, clean_text(f"{error}: {count}"), ln=True)
    pdf.ln(5)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(*grey_color)
    pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
    output_folder = "owl-pdf"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"dossier_{username}.pdf")
    pdf.output(output_path)
    print(f"\nReport saved: {output_path}")

def print_all_detections(detection_list):
    print("\n [+] Detections (summary):")
    for detection in detection_list:
        print("-" * 80)
        print(f"URL: {detection['url']}")
        print(f"Detected via: {', '.join(detection['detection_methods'])}")
        if detection['title_occurrences'] > 0:
            print(f"Title Occurrences: {detection['title_occurrences']}")
        if detection['description_occurrences'] > 0:
            print(f"Description Occurrences: {detection['description_occurrences']}")
        if detection['mention_occurrences'] > 0:
            print(f"Mentions/Tags Occurrences: {detection['mention_occurrences']}")
        profile = detection.get("profile_details", {})
        for key, value in profile.items():
            value_str = str(value)
            if key in ["followers", "following"]:
                print(f"{key.title()}: {value_str}")
            else:
                if len(value_str) > 300:
                    value_str = value_str[:300] + "..."
                print(f"{key.title()}: {value_str}")
        if PDF_OPTION:
            print("Full details are available in the PDF report.")
        print("-" * 80)

def animated_banner():
    banner = [
        "▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖",
        "▌          SOCIAL OWL         ▐",
        "▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘"
    ]
    for line in banner:
        colored_line = ''.join([random.choice(COLORS) + char for char in line])
        print(colored_line)
        time.sleep(1.2)

def main():
    global PDF_OPTION
    parser = argparse.ArgumentParser(description="Social Media Account Finder")
    parser.add_argument("username", help="Username to search (case-insensitive)")
    parser.add_argument("-f", "--file", default="config/social.txt", help="Platform list file")
    parser.add_argument("-pdf", "--pdf", action="store_true", help="Include PDF saving")
    args = parser.parse_args()
    PDF_OPTION = args.pdf
    # Ensure username is stripped; comparisons use username.lower() so case doesn't matter.
    username = args.username.strip()
    animated_banner()
    platforms = load_platforms(args.file)
    if platforms:
        print(f"\n{Fore.GREEN}• Starting scan for {Fore.CYAN}{username}{Fore.GREEN} across {len(platforms)} platforms •")
        errors, detections = generate_and_check_urls(username, platforms)
        if args.pdf:
            generate_pdf_report(username, detections, errors, len(platforms))
        if detections:
            print(f"\n{Fore.GREEN}✓ Scan complete: {len(detections)} accounts found")
        else:
            print(f"\n{Fore.YELLOW}⚠ No accounts found matching criteria")
        print_all_detections(detections)

if __name__ == "__main__":
    main()

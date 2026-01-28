import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_moltbot_skills():
    print("Execution started: Fetching data from ClawdHub...")
    
    url = "https://clawdhub.com/skills"
    # User-Agent header to mimic a real browser session
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Step 1: Request the webpage
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise an error if the request failed
        
        # Step 2: Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 3: Find all skill card containers
        # These are usually inside divs with specific classes on clawdhub.com
        cards = soup.find_all('div', class_='relative group')
        
        extracted_skills = []
        
        for card in cards:
            # Extract the title/name of the skill
            title_el = card.find('h3')
            if not title_el:
                continue
            name = title_el.get_text(strip=True)
            
            # Extract the description (usually the first paragraph found)
            desc_el = card.find('p')
            description = desc_el.get_text(strip=True) if desc_el else "No description provided."
            
            # Extract the GitHub repository URL
            github_link = card.find('a', href=re.compile(r'github\.com'))
            repo_url = github_link['href'] if github_link else "#"
            
            # Extract the Star count using regex to find numbers in the card text
            # This looks for numbers often associated with a star icon
            stars_text = card.get_text()
            stars_match = re.search(r'(\d+)', stars_text)
            stars_count = int(stars_match.group(1)) if stars_match else 0
            
            # Append structured data to our list
            extracted_skills.append({
                "name": name,
                "desc": description,
                "url": repo_url,
                "stars": stars_count
            })
            
        # Step 4: Prepare final data object including a timestamp
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": extracted_skills
        }
        
        # Step 5: Save the data to skills.json
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Scraped {len(extracted_skills)} skills and updated skills.json.")

    except Exception as e:
        print(f"Critical Error during scraping: {str(e)}")
        # Exit with error code so GitHub Actions knows it failed
        exit(1)

if __name__ == "__main__":
    scrape_moltbot_skills()

import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_skills():
    print("Starting data collection...")
    url = "https://clawdhub.com/skills"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selectors based on ClawdHub structure
        cards = soup.find_all('div', class_='relative group')
        skills_data = []

        for card in cards:
            name_el = card.find('h3')
            if not name_el: continue
            
            name = name_el.text.strip()
            
            # Extract description
            desc_el = card.find('p')
            description = desc_el.text.strip() if desc_el else "No description available"
            
            # Extract GitHub link
            github_link = card.find('a', href=re.compile(r'github\.com'))
            github_url = github_link['href'] if github_link else "#"

            # Extract star count
            # Looking for a number associated with the star icon
            stars_match = re.search(r'(\d+)', card.get_text())
            stars = int(stars_match.group(1)) if stars_match else 0

            skills_data.append({
                "name": name,
                "desc": description,
                "url": github_url,
                "stars": stars
            })

        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(skills_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Collected {len(skills_data)} skills.")

    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    scrape_skills()

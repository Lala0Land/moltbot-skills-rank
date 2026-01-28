import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Infinite Scraper...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        
        # --- NEW: Infinite Scroll Logic ---
        last_height = page.evaluate("document.body.scrollHeight")
        while True:
            print("Scrolling down...")
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(2000) # Wait for content to load
            
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break # Stop if we reached the bottom
            last_height = new_height
            
        print("Reached bottom of the page. Extracting data...")
        
        extracted_skills = []
        
        # --- NEW: Ultra-Broad Selectors ---
        # We look for any link that looks like a GitHub repo
        links = page.query_selector_all("a[href*='github.com/']")
        
        for link in links:
            href = link.get_attribute("href")
            # Move up to find the container div for this skill
            container = link.evaluate_handle("el => el.closest('div')").as_element()
            
            if container:
                # Get the name from the closest heading or strong text
                name_el = container.query_selector("h1, h2, h3, h4, p, span")
                name = name_el.inner_text().strip() if name_el else "Unknown"
                
                # Get description
                desc_el = container.query_selector("p")
                desc = desc_el.inner_text().strip() if desc_el else ""
                
                # Parse stars
                stars = 0
                full_text = container.inner_text()
                star_match = re.search(r'(\d+)', full_text)
                if star_match:
                    stars = int(star_match.group(1))

                extracted_skills.append({
                    "name": name,
                    "desc": desc,
                    "url": href,
                    "stars": stars
                })

        # Final Clean-up: Remove duplicates and empty entries
        unique_skills = {s['url']: s for s in extracted_skills if len(s['name']) > 2}.values()
        final_list = list(unique_skills)

        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Saved {len(final_list)} unique skills.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()

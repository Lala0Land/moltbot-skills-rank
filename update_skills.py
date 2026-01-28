import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Persistent Infinite Scraper...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 1000})
        page = context.new_page()
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        
        # --- IMPROVED: Infinite Scroll with Content Verification ---
        all_skills_data = {}
        previous_count = 0
        max_attempts_without_new = 5 # Stop if we scroll 5 times and see nothing new
        attempts = 0

        while attempts < max_attempts_without_new:
            # Scroll to the bottom of the current view
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            print(f"Scrolling... (Current unique skills found: {len(all_skills_data)})")
            
            # Wait for the network to be quiet and new elements to render
            page.wait_for_timeout(3000) 
            
            # Find all GitHub links currently on the page
            links = page.query_selector_all("a[href*='github.com/']")
            
            for link in links:
                href = link.get_attribute("href")
                if href not in all_skills_data:
                    # Move up to find the container box for this skill
                    container = link.evaluate_handle("el => el.closest('div')").as_element()
                    if container:
                        name_el = container.query_selector("h1, h2, h3, h4, p, span")
                        name = name_el.inner_text().strip() if name_el else "Unknown"
                        
                        desc_el = container.query_selector("p")
                        desc = desc_el.inner_text().strip() if desc_el else ""
                        
                        # Extract stars
                        full_text = container.inner_text()
                        star_match = re.search(r'(\d+)', full_text)
                        stars = int(star_match.group(1)) if star_match else 0

                        if len(name) > 2: # Filter out noise
                            all_skills_data[href] = {
                                "name": name,
                                "desc": desc,
                                "url": href,
                                "stars": stars
                            }

            # Check if we found anything new this round
            current_count = len(all_skills_data)
            if current_count > previous_count:
                attempts = 0 # Reset attempts if we found new data
                previous_count = current_count
            else:
                attempts += 1 # Increment if no new skills appeared
                print(f"No new skills detected. Attempt {attempts} of {max_attempts_without_new}...")

        final_list = list(all_skills_data.values())

        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Final Count: {len(final_list)} skills saved.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()

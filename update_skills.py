import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Snapshot Collector (Virtual List Mode)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        page.wait_for_timeout(5000)

        all_skills = {}

        # The Loop: Scroll a little, grab everything visible, repeat.
        for i in range(30): # More small steps instead of big jumps
            print(f"Collecting Snapshot {i+1}/30... (Total: {len(all_skills)})")
            
            # 1. Grab visible data using JS injection
            snapshot = page.evaluate("""() => {
                const items = [];
                // Look for every link to GitHub currently in the DOM
                const links = Array.from(document.querySelectorAll('a[href*="github.com/"]'));
                
                links.forEach(link => {
                    let parent = link.closest('div'); 
                    // Search for name and description in the container
                    const nameEl = parent ? parent.querySelector('h1, h2, h3, h4, h5, strong, p') : null;
                    const descEl = parent ? parent.querySelector('p:not(h1,h2,h3,h4,h5)') : null;
                    
                    if (nameEl && nameEl.innerText.length > 2) {
                        items.push({
                            name: nameEl.innerText.split('\\n')[0].trim(),
                            desc: desc_el ? desc_el.innerText.trim() : "",
                            url: link.href
                        });
                    }
                });
                return items;
            }""")

            # 2. Add new findings to our master dictionary
            for item in snapshot:
                if item['url'] not in all_skills:
                    all_skills[item['url']] = {
                        "name": item['name'],
                        "desc": item['desc'],
                        "url": item['url'],
                        "stars": 0
                    }

            # 3. Scroll down exactly one screen height
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            page.wait_for_timeout(1500) # Wait for the virtual list to swap items

        final_list = list(all_skills.values())
        
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Collector found {len(final_list)} skills.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()

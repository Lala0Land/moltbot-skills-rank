import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Deep Search Scraper...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        
        # We give the page a moment to settle
        page.wait_for_timeout(5000)

        all_skills = {}

        # Scroll loop to trigger all lazy-loading
        for i in range(15):  # Increased scroll count
            print(f"Deep Scroll Step {i+1}/15...")
            page.evaluate("window.scrollBy(0, 1500)")
            page.wait_for_timeout(2000)

            # --- JAVASCRIPT INJECTION: Find skills even in Shadow DOM ---
            # This script runs inside the browser and finds all GitHub links 
            # and their nearest text labels.
            found_data = page.evaluate("""() => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*="github.com/"]'));
                
                links.forEach(link => {
                    let parent = link.parentElement;
                    // Look up to 5 levels up for a container with text
                    let name = "Unknown";
                    let desc = "";
                    
                    for (let i = 0; i < 5; i++) {
                        if (parent) {
                            const h = parent.querySelector('h1, h2, h3, h4, h5, strong');
                            if (h) name = h.innerText;
                            const p = parent.querySelector('p');
                            if (p) desc = p.innerText;
                            if (name !== "Unknown") break;
                            parent = parent.parentElement;
                        }
                    }
                    
                    results.push({
                        name: name.trim(),
                        desc: desc.trim(),
                        url: link.href
                    });
                });
                return results;
            }""")

            for item in found_data:
                if item['url'] not in all_skills and len(item['name']) > 1:
                    all_skills[item['url']] = {
                        "name": item['name'],
                        "desc": item['desc'],
                        "url": item['url'],
                        "stars": 0 # Default if stars are hidden in icons
                    }

        final_list = list(all_skills.values())
        
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Deep Search found {len(final_list)} skills.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()

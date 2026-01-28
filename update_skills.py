import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Fixed Snapshot Harvester...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        page.wait_for_timeout(5000)

        all_skills_dict = {}
        
        # Incremental scrolling to bypass Virtual List unmounting
        for i in range(40): 
            # Capture using valid JavaScript .push() logic
            current_view_items = page.evaluate("""() => {
                const results = [];
                // Find all links that look like a GitHub repository
                const links = Array.from(document.querySelectorAll('a[href*="github.com/"]'));
                
                links.forEach(link => {
                    // Navigate up to find a container with text
                    const card = link.closest('div, section, li');
                    if (card) {
                        const titleEl = card.querySelector('h1, h2, h3, h4, h5, strong, b');
                        const descEl = card.querySelector('p, span');
                        
                        results.push({ 
                            url: link.href, 
                            name: titleEl ? titleEl.innerText.trim() : "Unknown Skill", 
                            desc: descEl ? descEl.innerText.trim() : "" 
                        });
                    }
                });
                return results;
            }""")

            # Add to our master list (prevents duplicates via URL key)
            for item in current_view_items:
                if item['url'] not in all_skills_dict and len(item['name']) > 2:
                    all_skills_dict[item['url']] = {
                        "name": item['name'].split('\n')[0], # Take first line of name
                        "desc": item['desc'][:200], # Cap description length
                        "url": item['url'],
                        "stars": 0
                    }

            # Small scroll to trigger the 'windowing' update
            page.mouse.wheel(0, 500) 
            page.wait_for_timeout(1000)
            
            if i % 5 == 0:
                print(f"Round {i}: Found {len(all_skills_dict)} total unique skills...")

        final_list = list(all_skills_dict.values())
        
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"SUCCESS! Harvested {len(final_list)} unique skills.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()

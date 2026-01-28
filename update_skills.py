import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_moltbot_skills():
    print("Launching Global Link Extractor...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Using a real User-Agent to prevent being treated as a bot
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        
        print("Navigating to ClawdHub...")
        page.goto("https://clawdhub.com/skills", wait_until="networkidle")
        page.wait_for_timeout(10000) # Give it 10 seconds to fully load EVERYTHING

        all_skills = {}

        for i in range(20):
            print(f"Extraction Round {i+1}/20... (Skills found: {len(all_skills)})")
            
            # This script grabs EVERY link on the page, even inside complex structures
            found_links = page.evaluate("""() => {
                const results = [];
                // Query ALL anchor tags on the page
                const allAnchors = Array.from(document.querySelectorAll('a'));
                
                allAnchors.forEach(a => {
                    const href = a.href || "";
                    if (href.includes('github.com/')) {
                        // Find the text near this link to use as a name
                        let textContent = a.innerText.trim();
                        let containerText = a.closest('div')?.innerText || "";
                        
                        results.push({
                            url: href,
                            rawText: containerText.split('\\n').slice(0, 3).join(' ') 
                        });
                    }
                });
                return results;
            }""")

            for item in found_links:
                if item['url'] not in all_skills:
                    # Clean up the name: take the first part of the text we found
                    clean_name = item['rawText'].split('⭐')[0].split('View')[0].strip()
                    if len(clean_name) > 2:
                        all_skills[item['url']] = {
                            "name": clean_name[:50], # Limit name length
                            "desc": "Moltbot Skill Tool",
                            "url": item['url'],
                            "stars": 0
                        }

            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(2000)

        final_list = list(all_skills.values())
        
        output_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "skills": final_list
        }
        
        with open('skills.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"DONE! Found {len(final_list)} unique skills.")
        browser.close()

if __name__ == "__main__":
    scrape_moltbot_skills()

import os
import time

from playwright.sync_api import sync_playwright



def main():
    print("Starting Webui test script...")
    
    with sync_playwright() as p:
        # Launch browser and create new page
        print("Launching browser...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to SillyTavern
        print("Navigating to SillyTavern...")
        page.goto("http://127.0.0.1:7860")
        
        # Wait for the chat interface to be loaded
        print("Waiting for chat interface...")
        page.wait_for_selector("[class='svelte-1f354aw pretty_scrollbar']", timeout=60000)
        time.sleep(1)
        print("Waiting for chat interface to be ready...")
       
        # Paste message
        print(f"Sending message...")
        page.fill("[class='svelte-1f354aw pretty_scrollbar']", "test")
        time.sleep(0.2)  # Small delay before clicking generate
        
    
        
        #Start gen
        print("Starting Generation...")
        page.click('[id="Generate"]')
        page.wait_for_selector('[id="stop"]')
    
        
        # Wait for generation to complete by monitoring the stop button visibility
        print("Waiting for generation to complete...")
        while True:
            # Get all stop buttons and check their visibility
            stop_buttons = page.locator('[id="stop"]').all()
            is_generating = any(button.is_visible() for button in stop_buttons)
                    
            if not is_generating:
                print("generation complete!")
                break
            time.sleep(0.1)  # Small delay to prevent CPU overuse
        
        # Get the last message
        print("Retrieving last message...")
        time.sleep(2)
        user = page.locator('[class="message-body"]').locator("nth=-1")
        last_message = user.inner_html()
        print(f"Last message received: {last_message}")
        
        # Keep browser open for a moment to verify
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    main()
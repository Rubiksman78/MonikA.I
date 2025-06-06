import os
import time

from playwright.sync_api import sync_playwright



def main():
    print("Starting SillyTavern test script...")
    
    with sync_playwright() as p:
        # Launch browser and create new page
        print("Launching browser...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to SillyTavern
        print("Navigating to SillyTavern...")
        page.goto("http://127.0.0.1:8000")
        
        # Wait for the chat interface to be loaded
        print("Waiting for chat interface...")
        page.wait_for_selector("#send_textarea", timeout=60000)
        time.sleep(3)
        #page.wait_for_load_state("networkidle")
        
        #NEED TO BE DONE : USE TEXT-GEN AS OPENAI KEY --API, UNCHECK IMPORT LOREBOOK DIALOGUE, CHECK AUTOLOAD LAST CHAT
        
           # Additional delay to handle startup popup
        #print("Waiting for startup popup to clear...")
        #time.sleep(2)
        
        # Paste message
        print("Sending test message...")
        page.fill("#send_textarea", "test")
        
        #Start gen
        print("Trying to click the button...")
        try:
            page.locator("#send_but").click()
        except Exception as e:
            print(f"Button press failed: {e}")
        page.wait_for_selector(".mes_stop", state="visible") #so that it doesn't see the generate button before it is clicked
        print("Stop button seen !")
        
        # Wait for generation to complete by monitoring the stop button visibility
        print("Waiting for generation to complete...")
        while True:
            stop_button = page.locator(".mes_stop")
            if not stop_button.is_visible():
                print("Generation complete!")
                break
            time.sleep(0.1)  # Small delay to prevent CPU overuse
        
        # Get the last message
        print("Retrieving last message...")
        paragraphs = page.locator(".mes.last_mes .mes_text p").all()
        last_message = "\n".join(p.inner_text() for p in paragraphs)
        print(f"Last message received: {last_message}")
        
        # Keep browser open for a moment to verify
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    main()

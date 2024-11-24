from playwright.sync_api import sync_playwright
import time

def create_playlist_and_add_videos(email, password, video_urls):
    with sync_playwright() as p:
        # Open the browser in headless mode
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Step 1: Go to YouTube and log in
        page.goto("https://www.youtube.com/account/")

        # Wait for the sign-in button to be visible before clicking
        # sign_in_button = page.locator("button[aria-label='Sign in']")
        # sign_in_button.wait_for(state="visible", timeout=10000)  # Wait up to 10 seconds
        # sign_in_button.click()

        # Step 2: Log in with your credentials
        page.fill("input[type='email']", email)
        page.click("button[class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 BqKGqe Jskylb TrZEUc lw1w4b']")  # Proceed to password screen
        page.wait_for_timeout(2000)  # wait for password input to show
        page.fill("input[type='password']", password)
        page.click("button[jsname='LgbsSe']")  # Submit the password

        # Step 3: Wait for the login to complete
        page.wait_for_selector("ytd-topbar-logo-renderer", timeout=10000)

        # Step 4: Create a new playlist
        page.goto("https://www.youtube.com/create_playlist")
        page.fill("input[aria-label='Name your playlist']", "My Playlist")
        page.click("button[aria-label='Create']")

        # Step 5: Add videos to the newly created playlist
        for video_url in video_urls:
            page.goto(video_url)
            page.click("button[aria-label='Save to playlist']")
            page.wait_for_selector("ytd-playlist-add-to-option-renderer", timeout=5000)
            page.click("yt-formatted-string#text", strict=True)  # Select the created playlist
            time.sleep(2)  # wait a bit before adding the next video

        print("Playlist created and videos added successfully!")
        
        # Close the browser
        browser.close()

# Replace these with your own credentials and video URLs
email = "sanniv.nitkkkr@gmail.com"
password = "Sanniv@2002"
video_urls = [
    "https://www.youtube.com/watch?v=VIDEO_ID_1",
    "https://www.youtube.com/watch?v=VIDEO_ID_2"
]

create_playlist_and_add_videos(email, password, video_urls)

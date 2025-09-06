#!/usr/bin/env python3
"""
RAILWAY.APP CSV AUTOMATION - PLAYWRIGHT VERSION
Uses Playwright instead of Selenium for better Railway.app compatibility
"""

import os
import time
import random
import schedule
from playwright.sync_api import sync_playwright
from datetime import datetime
import logging
import requests
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayPlaywrightDownloader:
    """Railway.app compatible CSV downloader using Playwright"""
    
    def __init__(self):
        self.alt_username = os.getenv('ALT_ROBLOX_USERNAME')
        self.alt_password = os.getenv('ALT_ROBLOX_PASSWORD')
        self.api_url = os.getenv('SPARKEDHOSTING_API_URL', 'http://208.87.101.142:5000/api')
        
        self.download_folder = "/tmp/roblox_downloads"
        self.browser = None
        self.page = None
        
        os.makedirs(self.download_folder, exist_ok=True)
        
        if not all([self.alt_username, self.alt_password]):
            raise ValueError("❌ Missing credentials")
        
        logger.info("✅ Railway Playwright downloader initialized")
        logger.info(f"📁 Download folder: {self.download_folder}")
        logger.info(f"🔗 API URL: {self.api_url}")
    
    def setup_browser(self):
        """Setup Playwright browser for Railway.app"""
        logger.info("🌐 Setting up Playwright browser...")
        
        try:
            playwright = sync_playwright().start()
            
            # Launch browser with Railway.app optimized settings
            self.browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images'
                ]
            )
            
            # Create new page
            self.page = self.browser.new_page()
            
            # Set download path
            self.page.set_default_navigation_timeout(60000)  # 60 seconds
            
            logger.info("✅ Playwright browser setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def safe_login(self):
        """Login to Roblox with alt account"""
        logger.info("🔐 Logging into Roblox...")
        
        try:
            # Go to login page
            self.page.goto("https://www.roblox.com/login")
            self.page.wait_for_timeout(5000)
            
            # Fill username
            username_input = self.page.locator("#login-username")
            username_input.clear()
            username_input.type(self.alt_username, delay=100)
            
            self.page.wait_for_timeout(2000)
            
            # Fill password
            password_input = self.page.locator("#login-password")
            password_input.clear()
            password_input.type(self.alt_password, delay=100)
            
            self.page.wait_for_timeout(3000)
            
            # Click login
            login_button = self.page.locator("#login-button")
            login_button.click()
            
            # Wait for login
            self.page.wait_for_timeout(15000)
            
            # Check success
            current_url = self.page.url
            if "create.roblox.com" in current_url or "home" in current_url or "dashboard" in current_url:
                logger.info("✅ Login successful")
                return True
            else:
                logger.error(f"❌ Login failed - URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def download_csv_files(self):
        """Download CSV files from Creator Dashboard"""
        logger.info("📥 Starting CSV download process...")
        
        try:
            # Navigate to creator dashboard
            self.page.goto("https://create.roblox.com/dashboard/creations")
            self.page.wait_for_timeout(10000)
            
            # Find and click first game
            game_links = self.page.locator("a[href*='experiences']")
            if game_links.count() == 0:
                logger.error("❌ No games found")
                return []
            
            logger.info(f"🎮 Found {game_links.count()} games")
            game_links.first.click()
            self.page.wait_for_timeout(10000)
            
            # Navigate to Analytics
            analytics_locators = [
                "a:has-text('Analytics')",
                "a[href*='analytics']",
                "span:has-text('Analytics')"
            ]
            
            analytics_found = False
            for locator in analytics_locators:
                try:
                    analytics_element = self.page.locator(locator)
                    if analytics_element.count() > 0:
                        analytics_element.first.click()
                        analytics_found = True
                        break
                except:
                    continue
            
            if not analytics_found:
                logger.error("❌ Could not find Analytics section")
                return []
            
            self.page.wait_for_timeout(10000)
            logger.info("✅ Navigated to Analytics section")
            
            # Setup download handling
            downloaded_files = []
            
            def handle_download(download):
                file_path = os.path.join(self.download_folder, download.suggested_filename)
                download.save_as(file_path)
                downloaded_files.append(file_path)
                logger.info(f"📄 Downloaded: {download.suggested_filename}")
            
            self.page.on("download", handle_download)
            
            # Find and click export buttons
            export_locators = [
                "button:has-text('Export')",
                "button:has-text('Download')",
                "a:has-text('Export')"
            ]
            
            export_buttons = []
            for locator in export_locators:
                try:
                    buttons = self.page.locator(locator)
                    for i in range(buttons.count()):
                        export_buttons.append(buttons.nth(i))
                except:
                    continue
            
            logger.info(f"🎯 Found {len(export_buttons)} export buttons")
            
            # Click export buttons (limit to 2)
            download_count = 0
            max_downloads = 2
            
            for button in export_buttons[:max_downloads]:
                try:
                    if download_count >= max_downloads:
                        break
                    
                    button.click()
                    self.page.wait_for_timeout(5000)
                    download_count += 1
                    logger.info(f"📊 Clicked export button {download_count}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Export button error: {e}")
                    continue
            
            # Wait for downloads to complete
            logger.info("⏳ Waiting for downloads...")
            self.page.wait_for_timeout(20000)
            
            # Find any CSV files that weren't caught by download handler
            csv_files = glob.glob(os.path.join(self.download_folder, "*.csv"))
            
            logger.info(f"✅ Total CSV files found: {len(csv_files)}")
            for csv_file in csv_files:
                file_size = os.path.getsize(csv_file)
                logger.info(f"  📄 {os.path.basename(csv_file)} ({file_size} bytes)")
            
            return csv_files
            
        except Exception as e:
            logger.error(f"❌ CSV download error: {e}")
            return []
    
    def upload_csv_to_sparkedhosting(self, csv_files):
        """Upload CSV files to SparkedHosting via API"""
        logger.info(f"📤 Uploading {len(csv_files)} files...")
        
        uploaded_count = 0
        
        for csv_file in csv_files:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                original_name = os.path.basename(csv_file)
                new_name = f"railway_{timestamp}_{original_name}"
                
                with open(csv_file, 'rb') as f:
                    files = {'files': (new_name, f.read(), 'text/csv')}
                
                response = requests.post(
                    f"{self.api_url}/upload-csv",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Uploaded: {new_name}")
                    uploaded_count += 1
                else:
                    logger.error(f"❌ Upload failed: HTTP {response.status_code}")
                
            except Exception as e:
                logger.error(f"❌ Upload error: {e}")
        
        return uploaded_count
    
    def cleanup(self):
        """Clean up browser and files"""
        logger.info("🧹 Cleaning up...")
        
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            
            for file in glob.glob(os.path.join(self.download_folder, "*")):
                os.remove(file)
            
            logger.info("✅ Cleanup complete")
        except:
            pass
    
    def run_automation(self):
        """Main automation function"""
        logger.info("🚀 Starting Railway CSV automation...")
        
        start_time = datetime.now()
        
        try:
            if not self.setup_browser():
                return False
            
            if not self.safe_login():
                return False
            
            csv_files = self.download_csv_files()
            if not csv_files:
                logger.warning("⚠️ No CSV files downloaded")
                return False
            
            uploaded_count = self.upload_csv_to_sparkedhosting(csv_files)
            
            duration = datetime.now() - start_time
            
            if uploaded_count > 0:
                logger.info(f"✅ Success! Processed {uploaded_count} files in {duration}")
                return True
            else:
                logger.error("❌ No files uploaded")
                return False
                
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    logger.info("🚂 RAILWAY CSV AUTOMATION - PLAYWRIGHT VERSION")
    
    try:
        downloader = RailwayPlaywrightDownloader()
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return
    
    # Schedule
    schedule.every().day.at("09:00").do(downloader.run_automation)
    schedule.every().day.at("21:00").do(downloader.run_automation)
    
    # Test run
    logger.info("🧪 Running test download...")
    success = downloader.run_automation()
    
    if success:
        logger.info("✅ Test successful!")
    else:
        logger.error("❌ Test failed - will retry at scheduled times")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()

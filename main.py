#!/usr/bin/env python3
"""
FIXED: Railway.app CSV Automation using Remote WebDriver
Expert solution using Railway's Selenium Standalone Chrome template
"""

import os
import time
import random
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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

class RailwayCSVDownloader:
    """Expert solution: Remote WebDriver using Railway's Selenium template"""
    
    def __init__(self):
        # Get environment variables
        self.alt_username = os.getenv('ALT_ROBLOX_USERNAME')
        self.alt_password = os.getenv('ALT_ROBLOX_PASSWORD')
        self.api_url = os.getenv('SPARKEDHOSTING_API_URL', 'http://208.87.101.142:5000/api')
        
        # NEW: Remote Selenium URL from Railway template
        self.selenium_remote_url = os.getenv('SELENIUM_REMOTE_URL', 'http://localhost:4444/wd/hub')
        
        # Download folder
        self.download_folder = "/tmp/roblox_downloads"
        self.driver = None
        
        # Create download folder
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Validate credentials
        if not all([self.alt_username, self.alt_password]):
            raise ValueError("❌ Missing ALT_ROBLOX_USERNAME or ALT_ROBLOX_PASSWORD environment variables")
        
        logger.info("✅ Railway CSV downloader initialized (EXPERT SOLUTION)")
        logger.info(f"📁 Download folder: {self.download_folder}")
        logger.info(f"🔗 API URL: {self.api_url}")
        logger.info(f"🌐 Selenium Remote URL: {self.selenium_remote_url}")
    
    def setup_remote_browser(self):
        """Connect to Railway Selenium service"""
        logger.info("🌐 Connecting to Railway Selenium service...")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            selenium_url = os.getenv('SELENIUM_REMOTE_URL', 'https://standalone-chrome-production-eb24.up.railway.app/wd/hub')
            
            logger.info(f"🔗 Connecting to: {selenium_url}")
            
            self.driver = webdriver.Remote(
                command_executor=selenium_url,
                options=chrome_options
            )
            
            logger.info("✅ Railway Selenium connected successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Railway Selenium connection failed: {e}")
            return False
    
    def setup_browserless_fallback(self):
        """EXPERT FALLBACK: Use Browserless service"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            # Browserless WebSocket connection
            browserless_url = "wss://chrome.browserless.io/webdriver"
            
            self.driver = webdriver.Remote(
                command_executor=browserless_url,
                options=chrome_options
            )
            
            logger.info("✅ Browserless fallback setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browserless fallback failed: {e}")
            return False
    
    def safe_login(self):
        """Login to Roblox with EXPERT timing strategies"""
        logger.info("🔐 Logging into Roblox with expert timing...")
        
        try:
            # Go to login page
            self.driver.get("https://www.roblox.com/login")
            
            # EXPERT: Use explicit waits instead of time.sleep()
            username_field = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "login-username"))
            )
            
            # Enter username with human-like timing
            username_field.clear()
            for char in self.alt_username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Wait and find password field
            password_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login-password"))
            )
            
            password_field.clear()
            for char in self.alt_password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(random.uniform(1, 3))
            
            # Click login button with explicit wait
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login-button"))
            )
            login_button.click()
            
            # Wait for login completion
            WebDriverWait(self.driver, 20).until(
                lambda driver: "login" not in driver.current_url.lower()
            )
            
            # Check success
            current_url = self.driver.current_url
            if any(indicator in current_url for indicator in ["create.roblox.com", "home", "dashboard"]):
                logger.info("✅ Login successful!")
                return True
            else:
                logger.error(f"❌ Login failed - URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def download_csv_files(self):
        """Download CSV files with EXPERT error handling"""
        logger.info("📥 Starting expert CSV download process...")
        
        try:
            # Navigate to creator dashboard
            self.driver.get("https://create.roblox.com/dashboard/creations")
            
            # EXPERT: Wait for page load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'experiences')]"))
            )
            
            # Find games
            game_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'experiences')]")
            
            if not game_links:
                logger.error("❌ No games found in dashboard")
                return []
            
            logger.info(f"🎮 Found {len(game_links)} games")
            
            # Click first game
            game_links[0].click()
            
            # Wait for game page load
            WebDriverWait(self.driver, 20).until(
                lambda driver: "experiences" in driver.current_url
            )
            
            # Navigate to Analytics with explicit wait
            analytics_link = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Analytics') or contains(@href, 'analytics')]"))
            )
            analytics_link.click()
            
            # Wait for analytics page
            WebDriverWait(self.driver, 20).until(
                lambda driver: "analytics" in driver.current_url
            )
            
            logger.info("✅ Navigated to Analytics section")
            
            # Find export buttons with improved selector
            export_buttons = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Export') or contains(text(), 'Download')]"))
            )
            
            logger.info(f"🎯 Found {len(export_buttons)} export buttons")
            
            # Download CSVs (limit to 2 for safety)
            download_count = 0
            max_downloads = 2
            
            for i, button in enumerate(export_buttons[:max_downloads]):
                try:
                    if download_count >= max_downloads:
                        break
                    
                    # Scroll to button and click
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    
                    # Wait for button to be clickable
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(button)
                    )
                    
                    logger.info(f"📊 Clicking export button {download_count + 1}")
                    button.click()
                    
                    # Wait between downloads
                    time.sleep(random.uniform(3, 6))
                    download_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Export button {i} error: {e}")
                    continue
            
            # Wait for downloads to complete
            logger.info("⏳ Waiting for downloads to complete...")
            time.sleep(15)
            
            # Find downloaded CSV files
            csv_files = glob.glob(os.path.join(self.download_folder, "*.csv"))
            
            logger.info(f"✅ Found {len(csv_files)} CSV files:")
            for csv_file in csv_files:
                file_size = os.path.getsize(csv_file)
                logger.info(f"  📄 {os.path.basename(csv_file)} ({file_size} bytes)")
            
            return csv_files
            
        except Exception as e:
            logger.error(f"❌ CSV download error: {e}")
            return []
    
    def upload_csv_to_sparkedhosting(self, csv_files):
        """Upload CSV files with expert retry logic"""
        logger.info(f"📤 Uploading {len(csv_files)} files to SparkedHosting...")
        
        uploaded_count = 0
        
        for csv_file in csv_files:
            # Retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Prepare file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_name = os.path.basename(csv_file)
                    new_name = f"railway_{timestamp}_{original_name}"
                    
                    # Read file
                    with open(csv_file, 'rb') as f:
                        file_content = f.read()
                    
                    # Upload
                    files = {'files': (new_name, file_content, 'text/csv')}
                    
                    logger.info(f"📤 Uploading: {new_name} (attempt {attempt + 1})")
                    
                    response = requests.post(
                        f"{self.api_url}/upload-csv",
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Successfully uploaded: {new_name}")
                        uploaded_count += 1
                        break
                    else:
                        logger.warning(f"⚠️ Upload attempt {attempt + 1} failed: HTTP {response.status_code}")
                        if attempt == max_retries - 1:
                            logger.error(f"❌ Upload failed after {max_retries} attempts")
                        else:
                            time.sleep(5)  # Wait before retry
                
                except Exception as e:
                    logger.warning(f"⚠️ Upload attempt {attempt + 1} error: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"❌ Upload failed after {max_retries} attempts")
                    else:
                        time.sleep(5)  # Wait before retry
        
        return uploaded_count
    
    def cleanup(self):
        """Expert cleanup with proper error handling"""
        logger.info("🧹 Expert cleanup...")
        
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Remote browser session closed")
        except Exception as e:
            logger.warning(f"⚠️ Browser cleanup warning: {e}")
        
        try:
            # Remove downloaded files
            for file in glob.glob(os.path.join(self.download_folder, "*")):
                os.remove(file)
            logger.info("✅ Temporary files cleaned")
        except Exception as e:
            logger.warning(f"⚠️ File cleanup warning: {e}")
    
    def run_automation(self):
        """EXPERT main automation with comprehensive error handling"""
        logger.info("🚀 Starting EXPERT Railway CSV automation...")
        
        start_time = datetime.now()
        
        try:
            # Setup remote browser
            if not self.setup_remote_browser():
                logger.error("❌ Remote browser setup failed, aborting automation")
                return False
            
            # Login with expert timing
            if not self.safe_login():
                logger.error("❌ Login failed, aborting automation")
                return False
            
            # Download CSVs with expert error handling
            csv_files = self.download_csv_files()
            
            if not csv_files:
                logger.warning("⚠️ No CSV files downloaded")
                return False
            
            # Upload with retry logic
            uploaded_count = self.upload_csv_to_sparkedhosting(csv_files)
            
            # Report results
            end_time = datetime.now()
            duration = end_time - start_time
            
            if uploaded_count > 0:
                logger.info(f"✅ EXPERT automation successful!")
                logger.info(f"📊 Processed {uploaded_count}/{len(csv_files)} files")
                logger.info(f"⏱️ Duration: {duration}")
                return True
            else:
                logger.error("❌ No files were uploaded successfully")
                return False
                
        except Exception as e:
            logger.error(f"❌ Expert automation failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """EXPERT main function with proper environment handling"""
    logger.info("=" * 60)
    logger.info("🚂 RAILWAY CSV AUTOMATION - EXPERT SOLUTION")
    logger.info("=" * 60)
    
    # Environment check
    logger.info("🔍 Expert environment check:")
    logger.info(f"  ALT_ROBLOX_USERNAME: {'✅ Set' if os.getenv('ALT_ROBLOX_USERNAME') else '❌ Missing'}")
    logger.info(f"  ALT_ROBLOX_PASSWORD: {'✅ Set' if os.getenv('ALT_ROBLOX_PASSWORD') else '❌ Missing'}")
    logger.info(f"  SPARKEDHOSTING_API_URL: {os.getenv('SPARKEDHOSTING_API_URL', 'Using default')}")
    logger.info(f"  SELENIUM_REMOTE_URL: {os.getenv('SELENIUM_REMOTE_URL', 'Using default')}")
    
    # Create downloader instance
    try:
        downloader = RailwayCSVDownloader()
    except Exception as e:
        logger.error(f"❌ Expert downloader setup failed: {e}")
        return
    
    # Schedule daily downloads
    schedule.every().day.at("09:00").do(downloader.run_automation)
    schedule.every().day.at("21:00").do(downloader.run_automation)
    
    logger.info("📅 Expert scheduled CSV downloads:")
    logger.info("   - Daily at 09:00 UTC")
    logger.info("   - Daily at 21:00 UTC")
    
    # Run test download immediately
    logger.info("🧪 Running expert test download...")
    success = downloader.run_automation()
    
    if success:
        logger.info("✅ Expert test download completed successfully!")
    else:
        logger.error("❌ Expert test download failed - will retry at scheduled times")
    
    # Keep scheduler running
    logger.info("🔄 Expert scheduler active, waiting for scheduled times...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()

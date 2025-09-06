#!/usr/bin/env python3
"""
RAILWAY.APP CSV AUTOMATION - FIXED VERSION
Compatible with Railway.app Chrome dependencies
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
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import logging
import requests
import glob
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayCSVDownloader:
    """Railway.app compatible CSV downloader with fixed ChromeDriver"""
    
    def __init__(self):
        # Get environment variables
        self.alt_username = os.getenv('ALT_ROBLOX_USERNAME')
        self.alt_password = os.getenv('ALT_ROBLOX_PASSWORD')
        self.api_url = os.getenv('SPARKEDHOSTING_API_URL', 'http://208.87.101.142:5000/api')
        
        # Railway.app folders
        self.download_folder = "/tmp/roblox_downloads"
        self.driver = None
        
        # Create download folder
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Validate credentials
        if not all([self.alt_username, self.alt_password]):
            raise ValueError("❌ Missing ALT_ROBLOX_USERNAME or ALT_ROBLOX_PASSWORD environment variables")
        
        logger.info("✅ Railway CSV downloader initialized")
        logger.info(f"📁 Download folder: {self.download_folder}")
        logger.info(f"🔗 API URL: {self.api_url}")
    
    def install_chrome_dependencies(self):
        """Install Chrome and ChromeDriver for Railway.app"""
        logger.info("🔧 Installing Chrome dependencies for Railway.app...")
        
        try:
            # Install Chrome
            commands = [
                "apt-get update",
                "apt-get install -y wget gnupg",
                "wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -",
                "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google.list",
                "apt-get update",
                "apt-get install -y google-chrome-stable",
                "apt-get install -y chromium-chromedriver"
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd.split(), check=True, capture_output=True)
                    logger.info(f"✅ Command executed: {cmd}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Command failed: {cmd} - {e}")
                    continue
            
            logger.info("✅ Chrome dependencies installed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chrome installation failed: {e}")
            return False
    
    def setup_browser(self):
        """Setup Chrome browser for Railway.app with dependency installation"""
        logger.info("🌐 Setting up Chrome browser...")
        
        # Try to install dependencies first
        self.install_chrome_dependencies()
        
        chrome_options = Options()
        
        # Railway.app requires these settings
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-css")
        
        # Additional Railway.app compatibility
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Download preferences
        prefs = {
            "download.default_directory": self.download_folder,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # User agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Try multiple ChromeDriver paths
            chromedriver_paths = [
                "/usr/bin/chromedriver",
                "/usr/local/bin/chromedriver",
                "/opt/google/chrome/chromedriver",
                None  # Let Selenium auto-detect
            ]
            
            for path in chromedriver_paths:
                try:
                    if path:
                        service = Service(executable_path=path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        self.driver = webdriver.Chrome(options=chrome_options)
                    
                    logger.info(f"✅ Chrome browser setup complete (path: {path or 'auto-detected'})")
                    return True
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed with ChromeDriver path {path}: {e}")
                    continue
            
            # If all paths fail, try downloading ChromeDriver
            logger.info("🔄 Attempting to download ChromeDriver...")
            return self.download_and_setup_chromedriver(chrome_options)
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def download_and_setup_chromedriver(self, chrome_options):
        """Download and setup ChromeDriver manually"""
        try:
            import zipfile
            import urllib.request
            
            # Download ChromeDriver
            chromedriver_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
            chromedriver_zip = "/tmp/chromedriver.zip"
            chromedriver_path = "/tmp/chromedriver"
            
            logger.info("📥 Downloading ChromeDriver...")
            urllib.request.urlretrieve(chromedriver_url, chromedriver_zip)
            
            # Extract ChromeDriver
            with zipfile.ZipFile(chromedriver_zip, 'r') as zip_ref:
                zip_ref.extractall("/tmp/")
            
            # Make executable
            os.chmod(chromedriver_path, 0o755)
            
            # Create driver with custom path
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("✅ ChromeDriver downloaded and setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromeDriver download failed: {e}")
            return False
    
    def safe_login(self):
        """Login to Roblox with alt account"""
        logger.info("🔐 Logging into Roblox...")
        
        try:
            # Go to login page
            self.driver.get("https://www.roblox.com/login")
            time.sleep(8)
            
            # Find username field
            username_field = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "login-username"))
            )
            
            # Enter username
            username_field.clear()
            for char in self.alt_username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(2)
            
            # Find password field
            password_field = self.driver.find_element(By.ID, "login-password")
            password_field.clear()
            for char in self.alt_password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(3)
            
            # Click login button
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(15)
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "create.roblox.com" in current_url or "home" in current_url or "dashboard" in current_url:
                logger.info("✅ Login successful")
                return True
            else:
                logger.error(f"❌ Login failed - Current URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def download_csv_files(self):
        """Download CSV files from Creator Dashboard"""
        logger.info("📥 Starting CSV download process...")
        
        try:
            # Navigate to creator dashboard
            self.driver.get("https://create.roblox.com/dashboard/creations")
            time.sleep(10)
            
            # Find games (experiences)
            game_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'experiences')]")
            
            if not game_links:
                logger.error("❌ No games found in dashboard")
                return []
            
            logger.info(f"🎮 Found {len(game_links)} games")
            
            # Click on first game (should be Tattoo Studio Tycoon)
            game_links[0].click()
            time.sleep(10)
            
            # Navigate to Analytics section
            analytics_found = False
            analytics_selectors = [
                "//a[contains(text(), 'Analytics')]",
                "//a[contains(@href, 'analytics')]",
                "//span[contains(text(), 'Analytics')]"
            ]
            
            for selector in analytics_selectors:
                try:
                    analytics_elements = self.driver.find_elements(By.XPATH, selector)
                    for element in analytics_elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            analytics_found = True
                            break
                    if analytics_found:
                        break
                except:
                    continue
            
            if not analytics_found:
                logger.error("❌ Could not find Analytics section")
                return []
            
            time.sleep(10)
            logger.info("✅ Navigated to Analytics section")
            
            # Look for export/download buttons
            export_selectors = [
                "//button[contains(text(), 'Export')]",
                "//button[contains(text(), 'Download')]",
                "//a[contains(text(), 'Export')]"
            ]
            
            export_buttons = []
            for selector in export_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    export_buttons.extend(buttons)
                except:
                    continue
            
            logger.info(f"🎯 Found {len(export_buttons)} potential export buttons")
            
            # Download CSVs (limit to 2 to be safe)
            download_count = 0
            max_downloads = 2
            
            for button in export_buttons[:max_downloads]:
                try:
                    if download_count >= max_downloads:
                        break
                    
                    if button.is_displayed() and button.is_enabled():
                        logger.info(f"📊 Clicking export button {download_count + 1}")
                        button.click()
                        time.sleep(8)
                        download_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Export button error: {e}")
                    continue
            
            # Wait for downloads to complete
            logger.info("⏳ Waiting for downloads to complete...")
            time.sleep(20)
            
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
        """Upload CSV files to SparkedHosting via API"""
        logger.info(f"📤 Uploading {len(csv_files)} files to SparkedHosting...")
        
        uploaded_count = 0
        
        for csv_file in csv_files:
            try:
                # Prepare file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                original_name = os.path.basename(csv_file)
                new_name = f"railway_{timestamp}_{original_name}"
                
                # Read file content
                with open(csv_file, 'rb') as f:
                    file_content = f.read()
                
                # Upload via API
                files = {'files': (new_name, file_content, 'text/csv')}
                
                logger.info(f"📤 Uploading: {new_name}")
                
                response = requests.post(
                    f"{self.api_url}/upload-csv",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Successfully uploaded: {new_name}")
                    uploaded_count += 1
                else:
                    logger.error(f"❌ Upload failed for {original_name}: HTTP {response.status_code}")
                    logger.error(f"Response: {response.text}")
                
            except Exception as e:
                logger.error(f"❌ Upload error for {os.path.basename(csv_file)}: {e}")
        
        return uploaded_count
    
    def cleanup(self):
        """Clean up browser and temporary files"""
        logger.info("🧹 Cleaning up...")
        
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")
        except:
            pass
        
        try:
            # Remove downloaded files
            for file in glob.glob(os.path.join(self.download_folder, "*")):
                os.remove(file)
            logger.info("✅ Temporary files cleaned")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")
    
    def run_automation(self):
        """Main automation function"""
        logger.info("🚀 Starting Railway CSV automation...")
        
        start_time = datetime.now()
        
        try:
            # Setup browser
            if not self.setup_browser():
                logger.error("❌ Browser setup failed, aborting automation")
                return False
            
            # Login to Roblox
            if not self.safe_login():
                logger.error("❌ Login failed, aborting automation")
                return False
            
            # Download CSV files
            csv_files = self.download_csv_files()
            
            if not csv_files:
                logger.warning("⚠️ No CSV files downloaded")
                return False
            
            # Upload to SparkedHosting
            uploaded_count = self.upload_csv_to_sparkedhosting(csv_files)
            
            # Report results
            end_time = datetime.now()
            duration = end_time - start_time
            
            if uploaded_count > 0:
                logger.info(f"✅ Automation successful!")
                logger.info(f"📊 Processed {uploaded_count}/{len(csv_files)} files")
                logger.info(f"⏱️ Duration: {duration}")
                return True
            else:
                logger.error("❌ No files were uploaded successfully")
                return False
                
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function for Railway.app deployment"""
    logger.info("=" * 60)
    logger.info("🚂 RAILWAY CSV AUTOMATION STARTING (FIXED VERSION)")
    logger.info("=" * 60)
    
    # Environment check
    logger.info("🔍 Environment check:")
    logger.info(f"  ALT_ROBLOX_USERNAME: {'✅ Set' if os.getenv('ALT_ROBLOX_USERNAME') else '❌ Missing'}")
    logger.info(f"  ALT_ROBLOX_PASSWORD: {'✅ Set' if os.getenv('ALT_ROBLOX_PASSWORD') else '❌ Missing'}")
    logger.info(f"  SPARKEDHOSTING_API_URL: {os.getenv('SPARKEDHOSTING_API_URL', 'Using default')}")
    
    # Create downloader instance
    try:
        downloader = RailwayCSVDownloader()
    except Exception as e:
        logger.error(f"❌ Downloader setup failed: {e}")
        return
    
    # Schedule daily downloads
    schedule.every().day.at("09:00").do(downloader.run_automation)
    schedule.every().day.at("21:00").do(downloader.run_automation)  # Backup time
    
    logger.info("📅 Scheduled CSV downloads:")
    logger.info("   - Daily at 09:00 UTC")
    logger.info("   - Daily at 21:00 UTC")
    
    # Run test download immediately
    logger.info("🧪 Running initial test download...")
    success = downloader.run_automation()
    
    if success:
        logger.info("✅ Test download completed successfully!")
    else:
        logger.error("❌ Test download failed - will retry at scheduled times")
    
    # Keep scheduler running
    logger.info("🔄 Scheduler active, waiting for scheduled times...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

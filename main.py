#!/usr/bin/env python3
"""
FIXED: Railway.app CSV Automation using Remote WebDriver
Complete solution with proper error handling and debugging
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
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime
import logging
import requests
import glob
import json
from pathlib import Path

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Railway logs to stdout
    ]
)
logger = logging.getLogger(__name__)

class RailwayCSVDownloader:
    """FIXED: Railway CSV automation with remote Selenium service"""
    
    def __init__(self):
        # Environment variables with validation
        self.alt_username = os.getenv('ALT_ROBLOX_USERNAME')
        self.alt_password = os.getenv('ALT_ROBLOX_PASSWORD')
        self.api_url = os.getenv('SPARKEDHOSTING_API_URL', 'http://208.87.101.142:5000/api')
        
        # FIXED: Use HTTP for Selenium hub (not HTTPS)
        self.selenium_url = os.getenv('SELENIUM_REMOTE_URL', 'http://localhost:4444/wd/hub')
        
        # FIXED: Railway-compatible paths
        self.download_folder = '/tmp/downloads'
        self.driver = None
        
        # Create download folder
        Path(self.download_folder).mkdir(parents=True, exist_ok=True)
        
        # Validate environment
        self._validate_environment()
        
        logger.info("🚂 Railway CSV downloader initialized")
        logger.info(f"📁 Download folder: {self.download_folder}")
        logger.info(f"🔗 API URL: {self.api_url}")
        logger.info(f"🌐 Selenium URL: {self.selenium_url}")
    
    def _validate_environment(self):
        """Validate all required environment variables"""
        missing = []
        
        if not self.alt_username:
            missing.append('ALT_ROBLOX_USERNAME')
        if not self.alt_password:
            missing.append('ALT_ROBLOX_PASSWORD')
            
        if missing:
            raise ValueError(f"❌ Missing environment variables: {', '.join(missing)}")
        
        logger.info("✅ Environment validation passed")
    
    def setup_remote_browser(self):
        """FIXED: Connect to Railway Selenium service with proper configuration"""
        logger.info("🌐 Connecting to Railway Selenium service...")
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # FIXED: Optimized Chrome options for Railway
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--headless")  # Essential for Railway
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                chrome_options.add_argument("--window-size=1920,1080")
                
                # FIXED: Download preferences for remote browser
                prefs = {
                    "download.default_directory": self.download_folder,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                chrome_options.add_experimental_option("prefs", prefs)
                
                # FIXED: Connection timeout and retry logic
                logger.info(f"🔌 Attempt {attempt + 1}: Connecting to {self.selenium_url}")
                
                self.driver = webdriver.Remote(
                    command_executor=self.selenium_url,
                    options=chrome_options
                )
                
                # Test connection with a simple command
                self.driver.set_page_load_timeout(30)
                self.driver.implicitly_wait(10)
                
                # Verify connection
                logger.info("🧪 Testing Selenium connection...")
                self.driver.get("https://httpbin.org/ip")
                
                logger.info("✅ Railway Selenium connected successfully!")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Connection attempt {attempt + 1} failed: {e}")
                
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error("❌ All connection attempts failed")
                    return False
        
        return False
    
    def test_selenium_connection(self):
        """Test Selenium service availability before main automation"""
        logger.info("🔍 Testing Railway Selenium service availability...")
        
        try:
            # Test if Selenium hub is responding
            test_url = self.selenium_url.replace('/wd/hub', '/status')
            logger.info(f"📡 Testing Selenium status at: {test_url}")
            
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Selenium service is responding")
                return True
            else:
                logger.warning(f"⚠️ Selenium service returned HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Selenium service test failed: {e}")
            return False
    
    def safe_login(self):
            """FIXED: Enhanced login with click interception fix"""
            logger.info("🔐 Logging into Roblox...")
            
            try:
                # Navigate to login page
                logger.info("📍 Navigating to Roblox login page...")
                self.driver.get("https://www.roblox.com/login")
                
                # Wait for page to fully load
                WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "login-username"))
                )
                
                # Enter username
                logger.info("✏️ Entering username...")
                username_field = self.driver.find_element(By.ID, "login-username")
                username_field.clear()
                time.sleep(0.5)
                username_field.send_keys(self.alt_username)
                
                # Enter password  
                logger.info("✏️ Entering password...")
                password_field = self.driver.find_element(By.ID, "login-password")
                password_field.clear()
                time.sleep(0.5)
                password_field.send_keys(self.alt_password)
                
                # Wait before clicking login
                time.sleep(random.uniform(1, 3))
                
                # FIXED: Better login button click handling
                logger.info("🖱️ Clicking login button...")
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "login-button"))
                )
                
                # Try multiple click methods
                try:
                    # Method 1: Regular click
                    login_button.click()
                except:
                    try:
                        # Method 2: JavaScript click (bypasses interception)
                        self.driver.execute_script("arguments[0].click();", login_button)
                    except:
                        # Method 3: Action chains click
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).move_to_element(login_button).click().perform()
                
                # Wait for login completion
                logger.info("⏳ Waiting for login completion...")
                WebDriverWait(self.driver, 30).until(
                    lambda driver: "login" not in driver.current_url.lower()
                )
                
                # Verify success
                current_url = self.driver.current_url
                logger.info(f"📍 Post-login URL: {current_url}")
                
                success_indicators = ["create.roblox.com", "home", "dashboard"]
                if any(indicator in current_url for indicator in success_indicators):
                    logger.info("✅ Login successful!")
                    return True
                else:
                    logger.error(f"❌ Login failed - unexpected URL: {current_url}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Login error: {e}")
                return False
    
    def download_csv_files(self):
        """FIXED: Enhanced CSV download with better navigation"""
        logger.info("📥 Starting CSV download process...")
        
        try:
            # Navigate to creator dashboard
            logger.info("📍 Navigating to creator dashboard...")
            self.driver.get("https://create.roblox.com/dashboard/creations")
            
            # Wait for page load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'experiences') or contains(text(), 'experience')]"))
            )
            
            # Find games with multiple selectors
            game_selectors = [
                "//a[contains(@href, 'experiences')]",
                "//div[contains(text(), 'Tattoo Studio')]/..",
                "//a[contains(text(), 'Tattoo')]"
            ]
            
            game_element = None
            for selector in game_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        game_element = elements[0]
                        logger.info(f"✅ Found game using selector: {selector}")
                        break
                except:
                    continue
            
            if not game_element:
                logger.error("❌ No games found in dashboard")
                return []
            
            # Click game
            logger.info("🖱️ Clicking on game...")
            self.driver.execute_script("arguments[0].click();", game_element)
            
            # Wait for game page
            WebDriverWait(self.driver, 30).until(
                lambda driver: "experiences" in driver.current_url or "games" in driver.current_url
            )
            
            logger.info("📍 Navigating to Analytics...")
            
            # Multiple selectors for Analytics link
            analytics_selectors = [
                "//a[contains(text(), 'Analytics')]",
                "//a[contains(@href, 'analytics')]",
                "//button[contains(text(), 'Analytics')]",
                "//div[contains(text(), 'Analytics')]/parent::a"
            ]
            
            analytics_element = None
            for selector in analytics_selectors:
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    analytics_element = element
                    logger.info(f"✅ Found Analytics using: {selector}")
                    break
                except:
                    continue
            
            if not analytics_element:
                logger.error("❌ Analytics section not found")
                return []
            
            # Click Analytics
            self.driver.execute_script("arguments[0].click();", analytics_element)
            
            # Wait for Analytics page
            WebDriverWait(self.driver, 30).until(
                lambda driver: "analytics" in driver.current_url
            )
            
            logger.info("✅ Successfully navigated to Analytics")
            
            # Look for export buttons with multiple strategies
            time.sleep(5)  # Let page fully load
            
            export_selectors = [
                "//button[contains(text(), 'Export')]",
                "//button[contains(text(), 'Download')]",
                "//a[contains(text(), 'Export')]",
                "//div[contains(text(), 'Export')]/following-sibling::button",
                "//*[@role='button' and contains(text(), 'Export')]"
            ]
            
            export_buttons = []
            for selector in export_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    export_buttons.extend(buttons)
                except:
                    continue
            
            # Remove duplicates
            export_buttons = list(set(export_buttons))
            
            logger.info(f"🎯 Found {len(export_buttons)} potential export buttons")
            
            if not export_buttons:
                logger.warning("⚠️ No export buttons found, trying alternative approach...")
                
                # Try right-click context menu approach
                try:
                    charts = self.driver.find_elements(By.XPATH, "//canvas | //svg | //*[contains(@class, 'chart')]")
                    if charts:
                        logger.info("🔍 Trying context menu approach...")
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).context_click(charts[0]).perform()
                        time.sleep(2)
                except:
                    pass
            
            # Download available CSVs (limit to 3 for safety)
            download_count = 0
            max_downloads = 3
            
            for i, button in enumerate(export_buttons[:max_downloads]):
                try:
                    if download_count >= max_downloads:
                        break
                    
                    logger.info(f"📊 Attempting download {download_count + 1}")
                    
                    # Scroll to button
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    
                    # Click export button
                    self.driver.execute_script("arguments[0].click();", button)
                    
                    # Wait for download
                    time.sleep(random.uniform(3, 8))
                    download_count += 1
                    
                    logger.info(f"✅ Export {download_count} triggered")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Export button {i} failed: {e}")
                    continue
            
            # Wait for downloads to complete
            logger.info("⏳ Waiting for downloads to complete...")
            time.sleep(15)
            
            # Find downloaded files
            csv_files = list(Path(self.download_folder).glob("*.csv"))
            
            logger.info(f"📁 Found {len(csv_files)} CSV files:")
            for csv_file in csv_files:
                file_size = csv_file.stat().st_size
                logger.info(f"  📄 {csv_file.name} ({file_size} bytes)")
            
            return [str(f) for f in csv_files]
            
        except Exception as e:
            logger.error(f"❌ CSV download error: {e}")
            return []
    
    def upload_csv_to_sparkedhosting(self, csv_files):
        """FIXED: Enhanced upload with better error handling"""
        logger.info(f"📤 Uploading {len(csv_files)} files to SparkedHosting...")
        
        if not csv_files:
            logger.warning("⚠️ No CSV files to upload")
            return 0
        
        uploaded_count = 0
        
        for csv_file in csv_files:
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # Prepare file with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_name = Path(csv_file).name
                    new_name = f"railway_{timestamp}_{original_name}"
                    
                    # Read file
                    with open(csv_file, 'rb') as f:
                        file_content = f.read()
                    
                    if len(file_content) == 0:
                        logger.warning(f"⚠️ Skipping empty file: {original_name}")
                        break
                    
                    # Prepare upload
                    files = {'files': (new_name, file_content, 'text/csv')}
                    
                    logger.info(f"📤 Uploading: {new_name} (attempt {attempt + 1}, {len(file_content)} bytes)")
                    
                    # Upload with timeout
                    response = requests.post(
                        f"{self.api_url}/upload-csv",
                        files=files,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Successfully uploaded: {new_name}")
                        uploaded_count += 1
                        break
                    else:
                        logger.warning(f"⚠️ Upload failed: HTTP {response.status_code}")
                        if attempt == max_retries - 1:
                            logger.error(f"❌ Upload failed after {max_retries} attempts")
                        else:
                            time.sleep(5 * (attempt + 1))  # Exponential backoff
                
                except Exception as e:
                    logger.warning(f"⚠️ Upload attempt {attempt + 1} error: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"❌ Upload failed after {max_retries} attempts: {e}")
                    else:
                        time.sleep(5 * (attempt + 1))
        
        return uploaded_count
    
    def cleanup(self):
        """Enhanced cleanup with proper error handling"""
        logger.info("🧹 Cleaning up...")
        
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser session closed")
        except Exception as e:
            logger.warning(f"⚠️ Browser cleanup warning: {e}")
        
        try:
            # Clean download folder
            for file_path in Path(self.download_folder).glob("*"):
                file_path.unlink()
            logger.info("✅ Temporary files cleaned")
        except Exception as e:
            logger.warning(f"⚠️ File cleanup warning: {e}")
    
    def run_automation(self):
        """ENHANCED: Main automation with comprehensive error handling and debugging"""
        logger.info("🚀 Starting Railway CSV automation...")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Test Selenium service
            if not self.test_selenium_connection():
                logger.error("❌ Selenium service not available, aborting")
                return False
            
            # Step 2: Setup remote browser
            if not self.setup_remote_browser():
                logger.error("❌ Remote browser setup failed, aborting")
                return False
            
            # Step 3: Login with enhanced error handling
            if not self.safe_login():
                logger.error("❌ Login failed, aborting")
                return False
            
            # Step 4: Download CSVs
            csv_files = self.download_csv_files()
            
            if not csv_files:
                logger.warning("⚠️ No CSV files downloaded")
                return False
            
            # Step 5: Upload to SparkedHosting
            uploaded_count = self.upload_csv_to_sparkedhosting(csv_files)
            
            # Report results
            end_time = datetime.now()
            duration = end_time - start_time
            
            if uploaded_count > 0:
                logger.info("🎉 AUTOMATION SUCCESSFUL!")
                logger.info(f"📊 Processed: {uploaded_count}/{len(csv_files)} files")
                logger.info(f"⏱️ Duration: {duration}")
                
                # Send success notification to Discord (optional)
                try:
                    self.send_success_notification(uploaded_count, len(csv_files), duration)
                except:
                    pass  # Don't fail automation for notification issues
                
                return True
            else:
                logger.error("❌ No files were uploaded successfully")
                return False
                
        except Exception as e:
            logger.error(f"❌ Automation failed with error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        finally:
            self.cleanup()
    
    def send_success_notification(self, uploaded_count, total_count, duration):
        """Send success notification to SparkedHosting API"""
        try:
            notification_data = {
                'message': f'🎉 Railway CSV automation successful!\n📊 Uploaded {uploaded_count}/{total_count} files\n⏱️ Duration: {duration}',
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            requests.post(
                f"{self.api_url}/automation-notification",
                json=notification_data,
                timeout=10
            )
        except:
            pass  # Notification failure shouldn't affect automation

def main():
    """Enhanced main function with proper environment and error handling"""
    logger.info("=" * 60)
    logger.info("🚂 RAILWAY CSV AUTOMATION - PRODUCTION VERSION")
    logger.info("=" * 60)
    
    # Environment diagnostics
    logger.info("🔍 Environment diagnostics:")
    env_vars = ['ALT_ROBLOX_USERNAME', 'ALT_ROBLOX_PASSWORD', 'SELENIUM_REMOTE_URL', 'SPARKEDHOSTING_API_URL']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'TOKEN' in var:
                masked = f"{value[:3]}***{value[-2:]}" if len(value) > 5 else "***"
                logger.info(f"  {var}: {masked}")
            else:
                logger.info(f"  {var}: {value}")
        else:
            logger.warning(f"  {var}: ❌ Missing")
    
    # Create downloader instance
    try:
        downloader = RailwayCSVDownloader()
    except Exception as e:
        logger.error(f"❌ Failed to create downloader: {e}")
        return
    
    # Check if this is Railway environment
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway.app")
        
        # Schedule daily automation
        schedule.every().day.at("09:00").do(downloader.run_automation)
        schedule.every().day.at("21:00").do(downloader.run_automation)
        
        logger.info("📅 Scheduled CSV automation:")
        logger.info("   - Daily at 09:00 UTC")
        logger.info("   - Daily at 21:00 UTC")
        
        # Run test immediately
        logger.info("🧪 Running initial test automation...")
        success = downloader.run_automation()
        
        if success:
            logger.info("✅ Test automation completed successfully!")
        else:
            logger.error("❌ Test automation failed - will retry at scheduled times")
        
        # Keep scheduler running
        logger.info("🔄 Scheduler active, waiting for scheduled times...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    else:
        # Local testing
        logger.info("💻 Running in local/test mode")
        logger.info("🧪 Executing single test run...")
        
        success = downloader.run_automation()
        
        if success:
            logger.info("✅ Test run completed successfully!")
        else:
            logger.error("❌ Test run failed")

if __name__ == "__main__":
    main()

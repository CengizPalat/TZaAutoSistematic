#!/usr/bin/env python3
"""
RAILWAY LOGIN DEBUGGER - Advanced Roblox Login Diagnostics
File: railway_login_debugger.py
Diagnoses exact login failure causes with screenshots and detailed analysis
"""

import os
import time
import json
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
import logging

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RobloxLoginDiagnostics:
    """Advanced diagnostics for Roblox login issues on Railway"""
    
    def __init__(self):
        # Environment variables
        self.alt_username = os.getenv('ALT_ROBLOX_USERNAME', 'ByddyY8rPao2124')
        self.alt_password = os.getenv('ALT_ROBLOX_PASSWORD')
        self.selenium_url = os.getenv('SELENIUM_REMOTE_URL', 'https://standalone-chrome-production-eb24.up.railway.app/wd/hub')
        
        # Diagnostic storage
        self.debug_data = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'selenium_url': self.selenium_url,
            'username': self.alt_username,
            'screenshots': [],
            'page_sources': [],
            'network_logs': [],
            'console_logs': [],
            'steps_completed': [],
            'errors_encountered': [],
            'final_diagnosis': '',
            'recommended_actions': []
        }
        
        self.driver = None
        self.step_counter = 0
    
    def setup_diagnostic_browser(self):
        """Setup Chrome with enhanced logging and debugging"""
        logger.info("🔧 Setting up diagnostic browser with enhanced logging...")
        
        chrome_options = Options()
        
        # Basic Railway compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Enhanced debugging options
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Anti-detection measures (in case Roblox is detecting automation)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Real user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Logging preferences for network and console
        chrome_options.add_experimental_option('goog:loggingPrefs', {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL'
        })
        
        try:
            self.driver = webdriver.Remote(
                command_executor=self.selenium_url,
                options=chrome_options
            )
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Execute anti-detection script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Diagnostic browser setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            self.debug_data['errors_encountered'].append(f"Browser setup failed: {e}")
            return False
    
    def capture_diagnostic_step(self, step_name, description=""):
        """Capture comprehensive diagnostic data for current step"""
        self.step_counter += 1
        timestamp = datetime.utcnow().isoformat()
        
        logger.info(f"📊 Step {self.step_counter}: {step_name}")
        
        step_data = {
            'step': self.step_counter,
            'name': step_name,
            'description': description,
            'timestamp': timestamp,
            'url': '',
            'title': '',
            'screenshot': '',
            'page_source': '',
            'console_logs': [],
            'network_logs': [],
            'page_errors': []
        }
        
        try:
            # Basic page info
            step_data['url'] = self.driver.current_url
            step_data['title'] = self.driver.title
            
            # Take screenshot
            screenshot_b64 = self.driver.get_screenshot_as_base64()
            step_data['screenshot'] = screenshot_b64
            logger.info(f"📸 Screenshot captured ({len(screenshot_b64)} chars)")
            
            # Capture page source
            page_source = self.driver.page_source
            step_data['page_source'] = page_source[:10000]  # Truncate for storage
            logger.info(f"📄 Page source captured ({len(page_source)} chars)")
            
            # Capture console logs
            try:
                console_logs = self.driver.get_log('browser')
                step_data['console_logs'] = [log for log in console_logs]
                if console_logs:
                    logger.info(f"📝 Captured {len(console_logs)} console logs")
            except:
                pass
            
            # Look for specific error indicators on page
            error_indicators = self.detect_page_errors()
            step_data['page_errors'] = error_indicators
            
            if error_indicators:
                logger.warning(f"⚠️ Page errors detected: {error_indicators}")
            
        except Exception as e:
            logger.error(f"❌ Failed to capture diagnostic data: {e}")
            step_data['capture_error'] = str(e)
        
        self.debug_data['steps_completed'].append(step_data)
        return step_data
    
    def detect_page_errors(self):
        """Detect specific Roblox login errors, CAPTCHA, 2FA, etc."""
        errors = []
        
        try:
            # Common Roblox error selectors
            error_selectors = [
                "//div[contains(@class, 'alert-warning')]",
                "//div[contains(@class, 'alert-danger')]", 
                "//div[contains(@class, 'error')]",
                "//span[contains(@class, 'text-error')]",
                "//div[contains(text(), 'incorrect')]",
                "//div[contains(text(), 'invalid')]",
                "//div[contains(text(), 'suspended')]",
                "//div[contains(text(), 'banned')]"
            ]
            
            for selector in error_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        errors.append({
                            'type': 'error_message',
                            'text': element.text,
                            'selector': selector
                        })
            
            # CAPTCHA detection
            captcha_selectors = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//*[contains(text(), 'robot')]",
                "//*[contains(text(), 'verify')]",
                "//*[contains(text(), 'challenge')]"
            ]
            
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    errors.append({
                        'type': 'captcha_detected',
                        'selector': selector,
                        'count': len(elements)
                    })
            
            # 2FA detection
            twofa_selectors = [
                "//input[contains(@placeholder, 'code')]",
                "//div[contains(text(), 'verification')]",
                "//div[contains(text(), '2-step')]",
                "//div[contains(text(), 'authenticator')]"
            ]
            
            for selector in twofa_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    errors.append({
                        'type': '2fa_required',
                        'selector': selector,
                        'count': len(elements)
                    })
            
            # Check for redirect to unexpected pages
            current_url = self.driver.current_url.lower()
            if 'challenge' in current_url or 'verify' in current_url or 'suspended' in current_url:
                errors.append({
                    'type': 'redirect_issue',
                    'url': current_url
                })
            
        except Exception as e:
            errors.append({
                'type': 'detection_error',
                'error': str(e)
            })
        
        return errors
    
    def test_multiple_login_approaches(self):
        """Test different login methods to find working approach"""
        logger.info("🧪 Testing multiple login approaches...")
        
        login_methods = [
            {
                'name': 'Standard Login Page',
                'url': 'https://www.roblox.com/login',
                'description': 'Normal login page approach'
            },
            {
                'name': 'Direct Login Page',
                'url': 'https://roblox.com/newlogin',
                'description': 'Alternative login page'
            },
            {
                'name': 'Mobile Login Page',
                'url': 'https://m.roblox.com/login',
                'description': 'Mobile version login'
            }
        ]
        
        for method in login_methods:
            logger.info(f"🔬 Testing: {method['name']}")
            
            try:
                # Navigate to login method
                self.driver.get(method['url'])
                time.sleep(3)
                
                # Capture state
                step_data = self.capture_diagnostic_step(
                    f"Login Method: {method['name']}", 
                    method['description']
                )
                
                # Try to find login form
                login_form_found = self.analyze_login_form()
                step_data['login_form_analysis'] = login_form_found
                
                # If form found, try login
                if login_form_found['form_found']:
                    login_result = self.attempt_login()
                    step_data['login_attempt_result'] = login_result
                    
                    if login_result['success']:
                        logger.info(f"✅ Login successful with {method['name']}")
                        return True
                else:
                    logger.warning(f"⚠️ No login form found for {method['name']}")
                
            except Exception as e:
                logger.error(f"❌ {method['name']} failed: {e}")
                self.debug_data['errors_encountered'].append(f"{method['name']}: {e}")
        
        return False
    
    def analyze_login_form(self):
        """Analyze the login form elements"""
        analysis = {
            'form_found': False,
            'username_field': None,
            'password_field': None,
            'login_button': None,
            'additional_elements': []
        }
        
        try:
            # Look for username field
            username_selectors = [
                "//input[@id='login-username']",
                "//input[@name='username']",
                "//input[@type='text']",
                "//input[contains(@placeholder, 'username')]",
                "//input[contains(@placeholder, 'Username')]"
            ]
            
            for selector in username_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    analysis['username_field'] = {
                        'selector': selector,
                        'id': elements[0].get_attribute('id'),
                        'name': elements[0].get_attribute('name'),
                        'placeholder': elements[0].get_attribute('placeholder')
                    }
                    break
            
            # Look for password field
            password_selectors = [
                "//input[@id='login-password']",
                "//input[@name='password']",
                "//input[@type='password']"
            ]
            
            for selector in password_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    analysis['password_field'] = {
                        'selector': selector,
                        'id': elements[0].get_attribute('id'),
                        'name': elements[0].get_attribute('name')
                    }
                    break
            
            # Look for login button
            button_selectors = [
                "//button[@id='login-button']",
                "//button[contains(text(), 'Log In')]",
                "//button[contains(text(), 'Login')]",
                "//input[@type='submit']"
            ]
            
            for selector in button_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    analysis['login_button'] = {
                        'selector': selector,
                        'id': elements[0].get_attribute('id'),
                        'text': elements[0].text
                    }
                    break
            
            # Check if we have all required elements
            analysis['form_found'] = (
                analysis['username_field'] is not None and 
                analysis['password_field'] is not None and 
                analysis['login_button'] is not None
            )
            
        except Exception as e:
            analysis['error'] = str(e)
            logger.error(f"❌ Login form analysis failed: {e}")
        
        return analysis
    
    def attempt_login(self):
        """Attempt login with enhanced error detection"""
        result = {
            'success': False,
            'steps_completed': [],
            'errors': [],
            'final_state': ''
        }
        
        try:
            # Step 1: Enter username
            logger.info("✏️ Entering username...")
            username_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login-username"))
            )
            username_field.clear()
            time.sleep(0.5)
            username_field.send_keys(self.alt_username)
            result['steps_completed'].append('username_entered')
            
            self.capture_diagnostic_step("Username Entered", f"Entered: {self.alt_username}")
            
            # Step 2: Enter password
            logger.info("✏️ Entering password...")
            password_field = self.driver.find_element(By.ID, "login-password")
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(self.alt_password)
            result['steps_completed'].append('password_entered')
            
            self.capture_diagnostic_step("Password Entered", "Password field filled")
            
            # Step 3: Click login button
            logger.info("🖱️ Clicking login button...")
            login_button = self.driver.find_element(By.ID, "login-button")
            
            # Try multiple click methods
            try:
                login_button.click()
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", login_button)
                except:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).move_to_element(login_button).click().perform()
            
            result['steps_completed'].append('login_button_clicked')
            self.capture_diagnostic_step("Login Button Clicked", "Attempted login submission")
            
            # Step 4: Wait for response with detailed monitoring
            logger.info("⏳ Monitoring login response...")
            
            # Check every 2 seconds for 30 seconds
            for i in range(15):  # 30 seconds total
                time.sleep(2)
                
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Check for success indicators
                if ("dashboard" in current_url or "home" in current_url or 
                    "create.roblox.com" in current_url):
                    result['success'] = True
                    result['final_state'] = f"Login successful - redirected to {current_url}"
                    logger.info(f"✅ Login successful! Redirected to: {current_url}")
                    break
                
                # Check for error indicators
                page_errors = self.detect_page_errors()
                if page_errors:
                    result['errors'].extend(page_errors)
                    result['final_state'] = f"Login failed - errors detected: {page_errors}"
                    logger.error(f"❌ Login errors detected: {page_errors}")
                    break
                
                # Check if still on login page (might indicate form error)
                if "login" in current_url and i > 5:  # After 10 seconds
                    result['final_state'] = f"Still on login page after {(i+1)*2} seconds"
                    logger.warning(f"⚠️ Still on login page after {(i+1)*2} seconds")
                
                # Capture periodic diagnostics
                if i % 3 == 0:  # Every 6 seconds
                    self.capture_diagnostic_step(
                        f"Login Wait Check {i+1}", 
                        f"URL: {current_url}, Title: {page_title}"
                    )
            
            if not result['success'] and not result['errors']:
                result['final_state'] = "Login timeout - no clear success or error indicators"
                logger.error("❌ Login timeout without clear error")
            
        except Exception as e:
            result['errors'].append(f"Login attempt exception: {e}")
            result['final_state'] = f"Login failed with exception: {e}"
            logger.error(f"❌ Login attempt failed: {e}")
        
        return result
    
    def run_comprehensive_diagnosis(self):
        """Run complete diagnostic suite"""
        logger.info("🚀 Starting comprehensive Roblox login diagnosis...")
        
        try:
            # Step 1: Setup browser
            if not self.setup_diagnostic_browser():
                return self.generate_diagnostic_report()
            
            self.capture_diagnostic_step("Browser Setup", "Diagnostic browser initialized")
            
            # Step 2: Test Selenium connection
            logger.info("🧪 Testing basic navigation...")
            self.driver.get("https://httpbin.org/ip")
            time.sleep(2)
            self.capture_diagnostic_step("Selenium Test", "Basic navigation test")
            
            # Step 3: Test different login approaches
            login_success = self.test_multiple_login_approaches()
            
            # Step 4: Generate diagnosis
            self.analyze_failure_causes()
            
            # Step 5: Generate recommendations
            self.generate_recommendations()
            
        except Exception as e:
            logger.error(f"❌ Comprehensive diagnosis failed: {e}")
            self.debug_data['errors_encountered'].append(f"Diagnosis failed: {e}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
        
        return self.generate_diagnostic_report()
    
    def analyze_failure_causes(self):
        """Analyze collected data to determine failure causes"""
        logger.info("🔍 Analyzing failure causes...")
        
        # Check for CAPTCHA
        captcha_detected = any(
            error.get('type') == 'captcha_detected' 
            for step in self.debug_data['steps_completed'] 
            for error in step.get('page_errors', [])
        )
        
        # Check for 2FA
        twofa_detected = any(
            error.get('type') == '2fa_required' 
            for step in self.debug_data['steps_completed'] 
            for error in step.get('page_errors', [])
        )
        
        # Check for account issues
        account_errors = [
            error for step in self.debug_data['steps_completed'] 
            for error in step.get('page_errors', [])
            if error.get('type') == 'error_message'
        ]
        
        # Analyze patterns
        if captcha_detected:
            self.debug_data['final_diagnosis'] = "CAPTCHA Challenge Detected"
        elif twofa_detected:
            self.debug_data['final_diagnosis'] = "2FA Verification Required"
        elif account_errors:
            self.debug_data['final_diagnosis'] = f"Account Error: {account_errors[0].get('text', 'Unknown')}"
        elif not any(step.get('login_form_analysis', {}).get('form_found', False) for step in self.debug_data['steps_completed']):
            self.debug_data['final_diagnosis'] = "Login Form Not Found"
        else:
            self.debug_data['final_diagnosis'] = "Login Timeout Without Clear Error"
    
    def generate_recommendations(self):
        """Generate specific recommendations based on diagnosis"""
        diagnosis = self.debug_data['final_diagnosis']
        
        if "CAPTCHA" in diagnosis:
            self.debug_data['recommended_actions'] = [
                "Implement CAPTCHA solving service (2captcha, AntiCaptcha)",
                "Add longer delays between login attempts",
                "Use different IP addresses/regions",
                "Implement session persistence to avoid repeated logins"
            ]
        elif "2FA" in diagnosis:
            self.debug_data['recommended_actions'] = [
                "Disable 2FA on alt account if possible",
                "Implement email verification handling",
                "Use app passwords if available",
                "Consider using authenticated session cookies"
            ]
        elif "Account Error" in diagnosis:
            self.debug_data['recommended_actions'] = [
                "Manually verify alt account credentials",
                "Check if account is suspended/locked",
                "Try password reset if needed",
                "Create new alt account if current one is compromised"
            ]
        elif "Login Form Not Found" in diagnosis:
            self.debug_data['recommended_actions'] = [
                "Update login selectors for current Roblox layout",
                "Test with different Roblox login URLs",
                "Check if Roblox has anti-bot measures",
                "Implement more robust element detection"
            ]
        else:
            self.debug_data['recommended_actions'] = [
                "Increase login timeout duration",
                "Add human-like behavior patterns",
                "Implement retry mechanisms",
                "Check network connectivity issues",
                "Monitor for Roblox service outages"
            ]
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        logger.info("📋 Generating diagnostic report...")
        
        # Calculate summary statistics
        total_steps = len(self.debug_data['steps_completed'])
        total_errors = len(self.debug_data['errors_encountered'])
        screenshots_captured = len([step for step in self.debug_data['steps_completed'] if step.get('screenshot')])
        
        report = {
            'diagnostic_summary': {
                'test_timestamp': self.debug_data['test_timestamp'],
                'total_steps_completed': total_steps,
                'total_errors_encountered': total_errors,
                'screenshots_captured': screenshots_captured,
                'final_diagnosis': self.debug_data['final_diagnosis'],
                'recommended_actions': self.debug_data['recommended_actions']
            },
            'environment_info': {
                'selenium_url': self.selenium_url,
                'alt_username': self.alt_username,
                'user_agent': "Chrome/120.0.0.0",
                'browser_settings': "Headless, No-sandbox, Anti-detection"
            },
            'detailed_steps': self.debug_data['steps_completed'],
            'errors_log': self.debug_data['errors_encountered'],
            'success_indicators': {
                'selenium_connection': True,
                'roblox_navigation': total_steps > 2,
                'login_form_found': any(step.get('login_form_analysis', {}).get('form_found') for step in self.debug_data['steps_completed']),
                'login_attempted': any('login_button_clicked' in step.get('login_attempt_result', {}).get('steps_completed', []) for step in self.debug_data['steps_completed'])
            }
        }
        
        # Save report
        try:
            report_filename = f"roblox_login_diagnosis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📄 Diagnostic report saved: {report_filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("🔍 ROBLOX LOGIN DIAGNOSTIC REPORT")
        print("="*60)
        print(f"⏰ Test Time: {report['diagnostic_summary']['test_timestamp']}")
        print(f"🎯 Final Diagnosis: {report['diagnostic_summary']['final_diagnosis']}")
        print(f"📊 Steps Completed: {report['diagnostic_summary']['total_steps_completed']}")
        print(f"❌ Errors Encountered: {report['diagnostic_summary']['total_errors_encountered']}")
        print(f"📸 Screenshots Captured: {report['diagnostic_summary']['screenshots_captured']}")
        print("\n💡 Recommended Actions:")
        for i, action in enumerate(report['diagnostic_summary']['recommended_actions'], 1):
            print(f"   {i}. {action}")
        print("="*60)
        
        return report

def main():
    """Main diagnostic execution"""
    print("🚀 Railway Roblox Login Diagnostics v1.0")
    print("🔍 Advanced debugging for login automation issues")
    print("="*60)
    
    # Validate environment
    if not os.getenv('ALT_ROBLOX_PASSWORD'):
        print("❌ ALT_ROBLOX_PASSWORD environment variable not set!")
        return
    
    diagnostics = RobloxLoginDiagnostics()
    report = diagnostics.run_comprehensive_diagnosis()
    
    # Upload report to SparkedHosting API for analysis
    try:
        api_url = "https://roblox.sparked.network/api/diagnostic-report"
        response = requests.post(api_url, json=report, timeout=30)
        if response.status_code == 200:
            print("📤 Diagnostic report uploaded to SparkedHosting API")
        else:
            print(f"⚠️ Failed to upload report: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not upload report: {e}")
    
    return report

if __name__ == "__main__":
    main()

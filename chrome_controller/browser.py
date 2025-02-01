import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import logging

class ChromeController:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ChromeController")

    def initialize(self):
        try:
            options = uc.ChromeOptions()
            self.driver = uc.Chrome(
                driver_executable_path=ChromeDriverManager().install(),
                options=options
            )
            return True
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False

    def cleanup(self):
        if self.driver:
            try:
                for handle in self.driver.window_handles[:]:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    except:
                        pass
                        
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
            finally:
                self.driver = None

    def __del__(self):
        self.cleanup()

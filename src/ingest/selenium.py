from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

class Selenium():

    _INSTANCE = None

    @staticmethod
    def get_instance(headless=True):
        if Selenium._INSTANCE is None:
            print("Did not find existing Selenium instance, initiating")
            Selenium._INSTANCE = Selenium(headless)
        return Selenium._INSTANCE

    @staticmethod
    def is_initiated():
        if Selenium._INSTANCE:
            return True
        return False

    def __init__(self, headless=True):
        self.driver = self.get_driver(headless)

    def get_driver(self, headless=True):
        options = webdriver.FirefoxOptions()
        options.set_headless(headless)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("media.volume_scale", "0.0")
        capa = DesiredCapabilities.FIREFOX
        capa["pageLoadStrategy"] = "none"
        driver = webdriver.Firefox(options=options, desired_capabilities=capa)
        return driver

    def crawl(self, url, wait_time=10, wait_target_selector="", manual_wait=5):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, wait_time)
        if wait_target_selector:
            wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, wait_target_selector)))
        time.sleep(manual_wait)
        return BeautifulSoup(self.driver.page_source, "lxml")

    def quit(self):
        self.driver.quit()
        Selenium._INSTANCE = None


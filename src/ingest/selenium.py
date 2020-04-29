from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Selenium():

    _INSTANCE = None

    @staticmethod
    def get_instance():
        if Selenium._INSTANCE is None:
            Selenium._INSTANCE = Selenium()
        return Selenium._INSTANCE

    def __init__(self):
        self.driver = self.get_driver()

    def get_driver(self, headless=True):
        options = webdriver.FirefoxOptions()
        options.set_headless(headless)
        capa = DesiredCapabilities.FIREFOX
        capa["pageLoadStrategy"] = "normal"
        driver = webdriver.Firefox(options=options, desired_capabilities=capa)
        return driver

    def crawl(self, url, wait_time=0):
        self.driver.get(url)
        WebDriverWait(self.driver, wait_time)
        return BeautifulSoup(self.driver.page_source, "lxml")

    def quit(self):
        self.driver.quit()


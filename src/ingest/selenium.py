from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, random

class Selenium():

    _INSTANCE = None

    @staticmethod
    def get_instance(headless=True, enable_proxy=False):
        if Selenium._INSTANCE is None:
            print("Did not find existing Selenium instance, initiating")
            print("HEADLESS: {}, USE_PROXY: {}".format(headless, enable_proxy))
            Selenium._INSTANCE = Selenium(headless, enable_proxy)
        return Selenium._INSTANCE

    @staticmethod
    def is_initiated():
        if Selenium._INSTANCE:
            return True
        return False

    def __init__(self, headless=True, enable_proxy=True):
        self.headless = headless
        self.vanilla = True
        self.enable_proxy = enable_proxy
        self.driver = self.get_driver()

    def enable_socks_proxy(self, profile):
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks", "127.0.0.1")
        profile.set_preference("network.proxy.socks_port", 10086)
        profile.set_preference("network.proxy.socks_version", 5)

    def get_driver(self):
        options = webdriver.FirefoxOptions()
        options.set_headless(self.headless)
        profile = webdriver.FirefoxProfile()
        if self.enable_proxy:
            self.enable_socks_proxy(profile)
        profile.set_preference("media.volume_scale", "0.0")
        capa = DesiredCapabilities.FIREFOX
        capa["pageLoadStrategy"] = "none"
        driver = webdriver.Firefox(firefox_profile=profile, options=options, desired_capabilities=capa)
        # chromerandom = [random.randint(1, 3), random.randint(2300, 2450), random.randint(10, 200)]
        # gen_header = {'User-Agent':"Mozilla/5.0 (Windows NT 6.{}; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.{}.{} Safari/537.36".format(*chromerandom)}
        # driver.header_overrides = gen_header
        # print(gen_header)
        return driver

    def reload_driver(self, refraction_period=15):
        if self.vanilla:
            self.vanilla = False
        else:
            self.driver.close()
            self.driver = self.get_driver()
            time.sleep(refraction_period)

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


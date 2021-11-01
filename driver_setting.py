from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def driver_init():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--headless")
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.maximize_window()
    return driver


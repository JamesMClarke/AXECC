from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

chromedriver = "/chromedriver"
option = webdriver.ChromeOptions()
option.binary_location = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
s = Service(chromedriver)
driver = webdriver.Chrome(service=s, options=option)

driver.get("https://google.com")
extensions = driver.execute_script("return window.chrome.runtime.getManifest();")
extension_list = []
for extension in extensions:
    extension_list.append(extension['name'])
print(extension_list)

time.sleep(3)
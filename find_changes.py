# The goal: 
# 1) download all extensions recorded in the list file
# 2) record statistical information for each extension in excel
# 3) install the extension in Chrome
# 4) browses to DOMtegrity file and initiates the ensuring process
# 5) records the browser log information

# Ehsan Toreini - May 2017


import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import pandas as pd

df = pd.read_csv('all_popular.csv')
extensions = df['File']

accessibility = 'accessibility_crx_files'
screen_reader = 'screen_reader_crx_files'

#print(rootdir)
chromedriver =  webdriver.Chrome()

capabilities = DesiredCapabilities.CHROME
capabilities['loggingPrefs'] = { 'browser':'ALL' }

print(chromedriver)

for extension in extensions:
    print(extension)
     
    #TODO: Find the location of CRX file and then load it
    options = webdriver.ChromeOptions()
    if os.path.isfile(os.path.join(accessibility, extension)):
        print('Accessibility')
        #options.add_extension(os.path.join(accessibility, extension))
    elif os.path.isfile(os.path.join(accessibility, extension)):
        print('Screen Reader')
        #options.add_extension(os.path.join(screen_reader, extension))
    else:
        print('File not found')
        break
    """
    driver = webdriver.Chrome(chromedriver, chrome_options=options)#, desired_capabilities=capabilities, service_args=["--verbose", "--log-path=E:\\qc1.log"])  # Optional argument, if not specified will search path.
    driver.get('https://localhost/')
    time.sleep(5) # Let the user actually see something!
    search_box = driver.find_element_by_id('buttonTest')
    #search_box.send_keys('ChromeDriver')
    search_box.click()
    #print(extension)
    list_file = open('InstalledExtensions.txt', 'a',encoding="utf8")
    list_file.write(extension+'\n')
    time.sleep(3) # Let the user actually see something!

    #print console log messages

    list_log = open('LogMessage.txt', 'a',encoding="utf8")
    
    for entry in driver.get_log('browser'):
        list_log.write(str(entry)+'\n')

    list_log.write('************************************************\n')
    driver.quit()
    """
	
#for root, dirs, files in os.walk(extension_dir):        
#    for file in files:
#        print(file)


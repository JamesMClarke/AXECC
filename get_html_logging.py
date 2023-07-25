"""
File to add logging to getting html from each page.

Need to run 'mitmproxy -s log_to_file.py' for it to log as well
"""
import time, os, logging, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import pandas as pd
import difflib


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/Users/jc02788/Documents/accessiblity_extensions/logfile.log')
logger.addHandler(handler)

logger.info("Starting %s" %(datetime.datetime.now()))

html_dir = 'html_files_new'

df = pd.read_csv('all_popular.csv')
extensions = df['File']
extensions = extensions[:-1]

accessibility = 'accessibility_crx_files'
screen_reader = 'screen_reader_crx_files'
current_dir = os.getcwd()

driver = webdriver.Chrome()
driver.get('http://localhost/')
baseline = driver.page_source
driver.quit()
with open(os.path.join(html_dir, 'baseline.html'), 'w') as outfile:
    outfile.write(baseline)

for extension in extensions:
    
    try:
        logger.info(extension)
        
        #Find the location of CRX file and then load it
        options = webdriver.ChromeOptions()
        if os.path.isfile(os.path.join(current_dir, accessibility, extension)):
            options.add_extension(os.path.join(accessibility, extension))
        elif os.path.isfile(os.path.join(current_dir, screen_reader, extension)):
            options.add_extension(os.path.join(screen_reader, extension))
        else:
            logger.info('File not found')

        driver = webdriver.Chrome(options=options)#, desired_capabilities=capabilities, service_args=["--verbose", "--log-path=E:\\qc1.log"])  # Optional argument, if not specified will search path.
        driver.get('http://localhost/')
        time.sleep(5) # Let the user actually see something!
        

        #Gets the code of the website and compare that against a baseline
        html = driver.page_source
        #with open(os.path.join(html_dir, extension+'.html'), 'w') as outfile:
        #    outfile.write(html)
        driver.quit()
        time.sleep(5)

    except KeyboardInterrupt:
        raise
    except Exception as error:
        logger.error("An error occurred")
        logger.error(error)
        
       
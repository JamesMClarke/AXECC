#TODO: Add loading bar and correct printing
import asyncio, logging, datetime, time, os, sys, threading, subprocess, argparse, csv
  
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib.request
from common import *

#Variables 
web_page = 'http://localhost:8081/'
extension_name = "None"
with open("current_ext.txt", "w") as f:
    f.write("None")
    f.close()

#Take input of csv file
parser = argparse.ArgumentParser("Visit webpage using extension")
parser.add_argument("csv", help="Input the name of the csv file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
parser.add_argument("-s")
args = parser.parse_args()
csv_file = args.csv
verbose = args.verbose


current_dir = os.getcwd()

csv_name = os.path.basename(csv_file).split(".")[0]

#Check if csv file exists
csv_file = os.path.join(current_dir,csv_file)
if(os.path.isfile(csv_file)):
    logging.info("File %s exists, starting to visit site with extension enabled" %(csv_name))
else:
    logging.error("File %s doesn't exists, stopping" %(csv_file))


current_dir = os.getcwd()
output_dir = os.path.join(current_dir, "html", csv_name)
create_directory(output_dir)

try:
    driver = webdriver.Chrome()
    driver.get(web_page)
    baseline = driver.page_source
    driver.quit()
    logging.info("Selenium and local server working")
except:
    logging.error("Selenium or web server not running")

with open(os.path.join(output_dir, 'baseline.html'), 'w') as outfile:
    outfile.write(baseline)

with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        extension = row[7]
        extension_name = extension.split('.')[0]
        print(extension_name)
        with open("current_ext.txt", "w") as f:
            f.write(extension_name)
            f.close()

        #Find the location of CRX file and then load it
        options = webdriver.ChromeOptions()
        ext_path = os.path.join(current_dir, "crx_files",csv_name, extension)
        if os.path.isfile(ext_path):
            options.add_extension(ext_path)
        else:
            logging.error(ext_path)
            logging.error('File not found')

        driver = webdriver.Chrome(options=options)#, desired_capabilities=capabilities, service_args=["--verbose", "--log-path=E:\\qc1.log"])  # Optional argument, if not specified will search path.
        driver.get(web_page)
        time.sleep(5) # Let the user actually see something!
        
        #Gets the code of the website and compare that against a baseline
        html = driver.page_source
        with open(os.path.join(outfile, extension+'.html'), 'w') as outfile:
            outfile.write(html)
        driver.quit()
        time.sleep(5)

sql = os.path.join(current_dir, "network")
create_directory(sql)
os.rename(os.path.join(current_dir,'temp.sqlite'), os.path.join(sql, csv_name+'.sqlite'))


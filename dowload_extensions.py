"""
Downloads extensions and saves info about them based on a txt file containing urls.
"""
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import urllib.request,re, argparse, time, os, sys
from tqdm import tqdm

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

current_dir=os.getcwd()

#Create dir for downloads

create_directory(os.path.join(current_dir,"crx_files"))

#Take input of txt file
parser = argparse.ArgumentParser("Download extenions")
parser.add_argument("urls", help="Input the name of the txt containing the urls.", type=str)
args = parser.parse_args()
urls_name = args.urls


#Check if csv file exists
url_file = os.path.join(current_dir,"extension_urls",urls_name+".txt")
if(os.path.isfile(url_file)):
    print("File %s exists, starting to download" %(urls_name))
else:
    print("File %s doesn't exists, stopping" %(url_file))
    sys.exit()

#Create download folder
download_folder = os.path.join(current_dir,"crx_files",urls_name)
create_directory(download_folder)

extension_list = open(url_file, 'r', encoding='utf-8') #,encoding="utf8"
extension_urls = extension_list.readlines()

# you may also want to remove whitespace characters like `\n` at the end of each line
extension_urls = [x.strip() for x in extension_urls]

options = FirefoxOptions()

options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", 'screen_reader')
#Need to set profile which is already logged in, for some extensions which include "mature content"
options.add_argument("-profile")
options.add_argument("/Users/jc02788/Library/Application Support/Firefox/Profiles/yqtf8iie.default-release")
#profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-chrome-extension")

driver = webdriver.Firefox(options=options)

extension_file = urls_name+".csv"

open(extension_file, 'w').close()
with tqdm(total=len(extension_urls)) as pbar:
    for ext in extension_urls:  
        # This section gets extension information 
        #try:
        driver.get(ext)
        list_file = open(extension_file, 'a', encoding='utf-8') #

        time.sleep(3) # Let the user actually see something!
        #try:
        extension_name = driver.find_element(by=By.CLASS_NAME, value='e-f-w').text
        print(extension_name)
        
        """except:
        extension_name = "Not Mentioned"
        #Make it so it errors out if it is not mentioned
        errors_file = open('Error URL.txt', 'a', encoding='utf-8')
        errors_file.write(ext+' -Getting name\n')
        errors_file.close()""" 

        try:
            extension_producer =  driver.find_element(by=By.CLASS_NAME, value='e-f-bb-K').find_element(by=By.CLASS_NAME, value='e-f-y').text
        except:
            try:
                extension_producer = driver.find_element(by=By.CLASS_NAME, value='C-b-p-D-Xe').text
            except:
                extension_producer = "Not Mentioned"

        try:
            extension_category = driver.find_element(by=By.CLASS_NAME, value='e-f-yb-w').find_element(by=By.CLASS_NAME, value='e-f-y').text
        except:
            extension_category = "Not Mentioned"

        try:
            extension_population = driver.find_element(by=By.CLASS_NAME, value='e-f-ih').text.replace(',', '')
            extension_population = extension_population.replace(' users', '')
        except:
            extension_population = "Not Mentioned"

        try:
            extension_ratings = driver.find_element(By.XPATH, "//meta[@itemprop='ratingValue']").get_attribute("content")
        except:
            extension_ratings = "Not Mentioned"
        
        try:
            extension_no_people_rated = driver.find_element(By.XPATH, "//meta[@itemprop='ratingCount']").get_attribute("content")
        except:
            extension_no_people_rated = "Not Mentioned"

        str2=ext.split('/')
        n = len(str2)
        url = "https://clients2.google.com/service/update2/crx?response=redirect&os=linux&arch=x64&os_arch=x86_64&nacl_arch=x86-64&prod=chromium&prodchannel=unknown&prodversion=91.0.4442.4&lang=en-US&acceptformat=crx2,crx3&x=id%3D"+ str2[n-1] + "%26installsource%3Dondemand%26uc"

        try:
            extension = '.crx'
            #Checks if the file already exists, if it does creates a versions with number at the end
            if os.path.isfile(os.path.join(download_folder,re.sub('[<>:"/\|?*,]',' ',extension_name))+".crx"):
                i = 1
                while os.path.isfile(os.path.join(download_folder,re.sub('[<>:"/\|?*,]',' ',extension_name))+'_'+str(i)+".crx"):
                    i += 1
                
                urllib.request.urlretrieve(url, os.path.join(download_folder,re.sub('[<>:"/\|?*,]',' ',extension_name))+'_'+str(i)+".crx")
                file_name  = re.sub('[<>:"/\|?*,]',' ',extension_name)+'_'+str(i)+".crx"
            else:
                urllib.request.urlretrieve(url, os.path.join(download_folder,re.sub('[<>:"/\|?*,]',' ',extension_name))+".crx")
                file_name = re.sub('[<>:"/\|?*,]',' ',extension_name)+".crx"
        except:
            errors_file = open('Error URL.txt', 'a', encoding='utf-8')
            errors_file.write(ext+' -Downloading extension\n')
            errors_file.close()
            #driver.get('http://chrome-extension-downloader.com/')

        list_file.write(re.sub('[<>:"/\|?*,]',' ',extension_name) + ',' + ext + ',' + extension_producer + ',' + extension_category + ',' + extension_population + ',' + extension_ratings + ',' + extension_no_people_rated + ',' + file_name+ '\n')
        list_file.close()
        #except:
        #    errors_file = open('Error URL.txt', 'a', encoding='utf-8')
        #    errors_file.write(ext+'\n')
        #    errors_file.close()

        time.sleep(2)
        pbar.update(1)

#TODO: Add checks that all extensions have been downloaded
driver.quit()  
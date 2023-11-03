"""
Downloads extensions and saves info about them based on a txt file containing urls.
TODO: Error handling for importing url files
"""
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException
import urllib.request,re, argparse, time, os, sys, csv
from tqdm import tqdm

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

current_dir=os.getcwd()

#Create dir for downloads
create_directory(os.path.join(current_dir,"crx_files"))

#Take input of txt file
parser = argparse.ArgumentParser("Download extenions")
parser.add_argument("urls", help="File contating the urls of to be downloaded", type=str)
parser.add_argument("-r",'--resume', dest="resume", help="Resume donwloading extensions", action='store_true')
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
urls = args.urls
resume = args.resume
verbos = args.verbose


#Get file name
urls_name = os.path.basename(urls).split(".")[0]

#Check if csv file exists
url_file = os.path.join(current_dir,urls)
if(not os.path.isfile(url_file)):
    print("File %s doesn't exists, stopping" %(url_file))
    sys.exit()

extension_file = urls_name+".csv"
if(resume):
    print("File %s exists, Resuming download" %(urls_name))
    with open(extension_file, 'r') as f:
        reader = csv.reader(f)
        already_done = str(list(reader))
else:
    open(extension_file, 'w').close()
    print("File %s exists, starting to download" %(urls_name))

#Create download folder
download_folder = os.path.join(current_dir,"crx_files",urls_name)
create_directory(download_folder)

#Get list of extensions
extension_list = open(url_file, 'r', encoding='utf-8') #,encoding="utf8"
extension_urls = extension_list.readlines()
extension_urls = [x.strip() for x in extension_urls]

options = FirefoxOptions()
#Need to set profile which is already logged in, for some extensions which include "mature content"
options.add_argument("-profile")
options.add_argument("/Users/jc02788/Library/Application Support/Firefox/Profiles/yqtf8iie.default-release")
driver = webdriver.Firefox(options=options)

no_extensions = len(extension_urls)

with tqdm(total=no_extensions) as pbar:
    for ext in extension_urls:
        if resume and ext in already_done:
            if verbos:
                tqdm.write("skipping %s"%(ext))
        else:
            if verbos:
                tqdm.write("Downloading %s "%(ext))
        
            #Try to get extension information
            for attempt in range(5):
                try:
                    driver.get(ext)
                    list_file = open(extension_file, 'a', encoding='utf-8') #

                    time.sleep(3) # Let the user actually see something!
                    extension_name = driver.find_element(by=By.CLASS_NAME, value='e-f-w').text

                    try:
                        extension_producer =  driver.find_element(by=By.CLASS_NAME, value='e-f-bb-K').find_element(by=By.CLASS_NAME, value='e-f-y').text
                    except:
                        try:
                            extension_producer = driver.find_element(by=By.CLASS_NAME, value='C-b-p-D-Xe').text
                        except:
                            extension_producer = "Not Mentioned"

                    extension_category = driver.find_element(by=By.CLASS_NAME, value='e-f-yb-w').find_element(by=By.CLASS_NAME, value='e-f-y').text

                    try:
                        extension_population = driver.find_element(by=By.CLASS_NAME, value='e-f-ih').text.replace(',', '')
                        extension_population = extension_population.replace(' users', '')
                    except:
                        extension_population = "Not Mentioned"

                    extension_ratings = driver.find_element(By.XPATH, "//meta[@itemprop='ratingValue']").get_attribute("content")

                    extension_no_people_rated = driver.find_element(By.XPATH, "//meta[@itemprop='ratingCount']").get_attribute("content")
                    break
                except Exception as e:
                    #tqdm.write("Error with selenium, trying again")
                    if attempt == 4:  # This is the last attempt
                        tqdm.write(extension_name+" couldn't be saved")
                        errors_file = open('Error URL.txt', 'a', encoding='utf-8')
                        errors_file.write(ext + " "+ str(e)+'\n')
                        errors_file.close()
                        raise  # Re-raise the last exception

            str2=ext.split('/')
            n = len(str2)
            url = "https://clients2.google.com/service/update2/crx?response=redirect&os=linux&arch=x64&os_arch=x86_64&nacl_arch=x86-64&prod=chromium&prodchannel=unknown&prodversion=91.0.4442.4&lang=en-US&acceptformat=crx2,crx3&x=id%3D"+ str2[n-1] + "%26installsource%3Dondemand%26uc"
            #Try to download file
            for attempt in range(5):
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
                    break
                except:
                    if attempt == 4:  # This is the last attempt
                        errors_file = open('Error URL.txt', 'a', encoding='utf-8')
                        errors_file.write(ext+' -Downloading extension\n')
                        tqdm.write(extension_name+" couldn't be downloaded")
                        errors_file.close()
                        file_name = "error"
                        #driver.get('http://chrome-extension-downloader.com/')
                    
            #Write extension details to file
            list_file.write(re.sub('[<>:"/\|?*,]',' ',extension_name) + ',' + ext + ',' + re.sub('[<>:"/\|?*,]',' ',extension_producer) + ',' + extension_category + ',' + extension_population + ',' + extension_ratings + ',' + extension_no_people_rated + ',' + file_name+ '\n')
            list_file.close()
            #time.sleep(2)
        
        #Update progess bard
        pbar.update(1)

driver.quit()  

#Check all files have been downloaded
files_in_dir = len([d for d in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, d))])

if(no_extensions == files_in_dir):
    print("All extensions have been downloaded")
else:
    print("Some extensions have not been dowloaded")
    print("Check above or in Error URL for details")
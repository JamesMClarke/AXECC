from common import *
from tqdm import tqdm
import urllib.request, argparse, time, os, re, sys, shutil
from bs4 import BeautifulSoup
from sqlite3 import Error

def create_table(conn):
    try:
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS extensions (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text,
                                        url text,
                                        producer_name text,
                                        producer_company text,
                                        producer_address text,
                                        category text,
                                        population int,
                                        rating int,
                                        no_ratings,
                                        file text
                                    ); """)
    except Error as e:
        print(e)

def create_ext(conn, extension_name, url, producer_name, producer_company, producer_address, extension_category, extension_population, extension_ratings, no_ratings, file_name):
    sql = ''' INSERT INTO extensions(name, url, producer_name, producer_company, producer_address, category, population, rating, no_ratings, file) VALUES (?,?,?,?,?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, (re.sub('[<>:"/\|?*,]',' ',extension_name), url, re.sub('[<>:"/\|?*,]',' ',producer_name), re.sub('[<>:"/\|?*,]',' ',producer_company), re.sub('[<>:"/\|?*,]',' ',producer_address), extension_category, re.sub(",",'',extension_population), extension_ratings, re.sub("ratings",'',no_ratings), file_name))
    conn.commit()


current_dir = os.getcwd()
crx_folder = os.path.join(current_dir,"crx_files")

#Create dir for all crx files
create_directory(crx_folder)

#Take input of txt file
parser = argparse.ArgumentParser("Download extenions")
parser.add_argument("urls", help="File contating the urls of to be downloaded", type=str)
parser.add_argument("-r",'--resume', dest="resume", help="Resume donwloading extensions", action='store_true')
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
urls = args.urls
resume = args.resume
verbose = args.verbose

#Get file name
urls_name = os.path.basename(urls).split(".")[0]

#Check if txt file exists
url_file = os.path.join(current_dir,urls)
if(not os.path.isfile(url_file)):
    print("File %s doesn't exists, stopping" %(url_file))
    sys.exit()

#extension_file = urls_name+".csv"
db_file = urls_name+".sqlite"
conn = create_connection(db_file)

#Create download folder
download_folder = os.path.join(crx_folder, urls_name)

if(resume):
    print("File %s exists, Resumeing download" %(urls_name))
    already_done = select_column(conn, 'url')
else:
    print("File %s exists, starting to download" %(urls_name))
    drop_table(conn,'extensions')
    if os.path.exists(download_folder):
        # Delete the empty folder using os.rmdir()
        shutil.rmtree(download_folder)

create_table(conn)
create_directory(download_folder)


#Get list of extensions
extension_list = open(url_file, 'r', encoding='utf-8') #,encoding="utf8"
extension_urls = extension_list.readlines()
extension_urls = [x.strip() for x in extension_urls]

no_extensions = len(extension_urls)

with tqdm(total=no_extensions) as pbar:
    for url in extension_urls:
        if resume and url in already_done:
            if verbose:
                tqdm.write("skipping %s"%(url))
        else:
            if verbose:
                tqdm.write("Downloading %s "%(url))
        #get html
        page = urllib.request.urlopen(url)

        # parse the html using beautiful soup and store in variable `soup`
        soup = BeautifulSoup(page, 'html.parser')

        name_box = soup.find('h1', attrs={'class': 'Pa2dE'})
        extension_name = name_box.text.strip()

        producer_box = soup.find('div', attrs={'class':'C2WXF'})
        #print(list(producer_box.stripped_strings))
        producer_name, producer_company, producer_address = producer_box.stripped_strings
        producer_address = producer_address.replace("\n", '')


        category_box = soup.find('a', attrs={'class':'gqpEIe bgp7Ye'})
        extension_category = category_box.text.strip()

        population_box = soup.find(string=lambda text: text and re.search(r"\d+,?\d+ users", text))
        extension_population = population_box.text.strip()
        extension_population = extension_population.replace(' users', '')

        ratings_box = soup.find('span', attrs={'class':'Vq0ZA'})
        extension_ratings = ratings_box.text.strip()

        no_ratings_box = soup.find('p', attrs={'class': 'xJEoWe'})
        no_ratings = no_ratings_box.text.strip()

        str2=url.split('/')
        n = len(str2)
        download_url = "https://clients2.google.com/service/update2/crx?response=redirect&os=linux&arch=x64&os_arch=x86_64&nacl_arch=x86-64&prod=chromium&prodchannel=unknown&prodversion=91.0.4442.4&lang=en-US&acceptformat=crx2,crx3&x=id%3D"+ str2[n-1] + "%26installsource%3Dondemand%26uc"
        #Try to download file
        for attempt in range(5):
            try:
                extension = '.crx'
                file = re.sub('[<>:"/\|?*,.]',' ',extension_name)
                #Checks if the file already exists, if it does creates a versions with number at the end
                if os.path.isfile(os.path.join(download_folder, file+".crx")):
                    i = 1
                    while os.path.isfile(os.path.join(download_folder,file+'_'+str(i)+".crx")):
                        i += 1

                    urllib.request.urlretrieve(download_url, os.path.join(download_folder,file+'_'+str(i)+".crx"))
                    file_name  = os.path.join(file+'_'+str(i)+".crx")
                else:
                    urllib.request.urlretrieve(download_url, os.path.join(download_folder,file+".crx"))
                    file_name = file+".crx"
                break
            except Exception as e:
                if attempt == 4:  # This is the last attempt
                    errors_file = open('Error URL.txt', 'a', encoding='utf-8')
                    errors_file.write(ext+' -Downloading extension\n')
                    errors_file.write(str(e))
                    tqdm.write(extension_name+" couldn't be downloaded")
                    errors_file.close()
                    file_name = "error"
                    #driver.get('http://chrome-extension-downloader.com/')

        #Write extension details to file
        #list_file.write(re.sub('[<>:"/\|?*,]',' ',extension_name) + ',' + url + ',' + re.sub('[<>:"/\|?*,]',' ',producer_name) + ',' + re.sub('[<>:"/\|?*,]',' ',producer_company) + ',' + re.sub('[<>:"/\|?*,]',' ',producer_address) + ',' + extension_category + ',' + re.sub(",",'',extension_population) + ',' + extension_ratings + ',' + re.sub("ratings",'',no_ratings) + ',' + file_name+ '\n')
        #list_file.close()
        create_ext(conn, extension_name, url, producer_name, producer_company, producer_address, extension_category, extension_population, extension_ratings, no_ratings, file_name)
        #time.sleep(2)

    #Update progess bard
    pbar.update(1)

conn.close()

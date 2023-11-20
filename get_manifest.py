import os, json, re, csv, argparse, sys
from tqdm import tqdm
from time import sleep
from common import *

#List of all possible permissions as of 3/11/23
Perms = ['accessibilityFeatures.modify','accessibilityFeatures.read','bookmarks',
         'clipboardRead','clipboardWrite','contentSettings','debugger','declarativeNetRequest','declarativeNetRequestFeedback','desktopCapture',
         'downloads','favicon','geolocation','history','identity.email','management','nativeMessaging','notifications','pageCapture','privacy',
         'proxy','sessions','history','tabs','system.storage','tabCapture','tabGroups','topSites','ttsEngine','webAuthenticationProxy','webNavigation',
         'storage','activeTab','alarms','idle','unlimitedStorage','offscreen','scripting','declarativeNetRequestWithHostAccess','identity',
         'webRequest','webRequestBlocking','contextMenus','browsingData','background','power','contextMenus','declarativeContent','tts',
         'cookies','commands','gcm','chrome://favicon/','fileBrowserHandler','sidePanel','system.display','fontSettings',
         'None']

no_perms = len(Perms)

parser = argparse.ArgumentParser("Get manifest from extension")
parser.add_argument("csv", help="Input the name of the csv file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
csv_file = args.csv
verbose = args.verbose

current_dir = os.getcwd()
csv_name = os.path.basename(csv_file).split(".")[0]

#Check if csv file exists
csv_file = os.path.join(current_dir,csv_file)
if(os.path.isfile(csv_file)):
    print("File %s exists, starting to get manifests" %(csv_name))
else:
    print("File %s doesn't exists, stopping" %(csv_file))
    sys.exit()

dir = os.path.join(current_dir,"preprocessed",csv_name)

#Create output dirs
create_directory(os.path.join(current_dir,"manifest"))
output_dir = os.path.join(current_dir,"manifest",csv_name)
create_directory(output_dir)

#Create file from permissions and hosts
perm_file = os.path.join(output_dir,"permissions_and_info.csv")
host_file = os.path.join(output_dir,"hosts.csv")

#Write headings to permission file
perm_writer = open(perm_file, 'w', encoding='utf-8')
#Write headings for info about them and manifest
perm_writer.write("Name, url, producer, category, population, rating, no_rated, filename, manifest_version,")

#Write perms headings 
for p in Perms:
    perm_writer.write(str(p) + ',')

perm_writer.write("\n")
perm_writer.close()

with open(csv_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    no_rows = len(rows)
    hosts = {}
    with tqdm(total=no_rows) as pbar:
        for row in rows:
            filename = str(row[7]).split('.')[0]
            if verbose:
                tqdm.write("Checking %s" %str(filename))

            try:
                with open(os.path.join(dir, filename, 'manifest.json')) as f:
                    data = json.load(f)
                    try:
                        permissions = data["permissions"]
                    except:
                        permissions = ['None']

                    try:
                        host_permissions = data["host_permissions"]
                    except:
                        host_permissions = ['None']

                    #Get manifest version
                    manifest_version = data['manifest_version']
            except: 
                permissions = ['Error']
                host_permissions = ['Error']
                manifest_version = 'Error'
            
            permission_list = [0 for _ in range(no_perms)]

            for p in permissions:
                if p in Perms:
                    permission_list[Perms.index(p)] = 1
                else:
                    if p in hosts:
                        hosts[p] += 1
                    else:
                        hosts[p] = 1
                    
            for h in host_permissions:
                if h != 'None':
                    if h in hosts:
                        hosts[h] += 1
                    else:
                        hosts[h] = 1
            if verbose:
                tqdm.write(str(permission_list))
            
            #Open file
            perm_writer = open(perm_file, 'a', encoding='utf-8')
            
            #Write existing info
            for i in row:
                perm_writer.write(i + ',')

            #Write manifest version
            perm_writer.write(str(manifest_version)+ ',')

            #Write permissions
            for p in permission_list:
                perm_writer.write(str(p) + ',')
            perm_writer.write('\n')
            perm_writer.close()

            pbar.update(1)

if verbose:
    print(hosts)

#Sort hosts
hosts = sort_dic(hosts)

#Create host file
with open(host_file, 'w') as csvfile:  
    # creating a csv dict writer object  
    writer = csv.DictWriter(csvfile, fieldnames = hosts.keys())  

    # writing headers (field names)  
    writer.writeheader()  

    # writing data rows  
    writer.writerow(hosts) 
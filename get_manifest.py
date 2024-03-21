import os, json, re, csv, argparse, sys
from tqdm import tqdm
from time import sleep
from common import *

def create_table_from_list(conn, column_names):
    # Check if list is empty
    if not column_names:
        raise ValueError("list_data cannot be empty")
    # Construct CREATE TABLE statement with placeholders for values
    create_table_stmt = f"""CREATE TABLE IF NOT EXISTS permissions (
        name text,
        {', '.join([f'`{col}` INTEGER' for col in column_names])}
    );"""
    cursor = conn.cursor()
    # Execute CREATE TABLE statement
    cursor.execute(create_table_stmt)

def insert_list(conn, name, column_names, list_data):
    cursor = conn.cursor()
    # Insert data into the table using parameterized queries for security
    insert_stmt = f"""INSERT INTO permissions (name,{', '.join([f'`{col}`' for col in column_names])}) VALUES (?,{', '.join(['?'] * len(column_names))});"""
    cursor.execute(insert_stmt, [name]+list_data)

    # Save changes to the database
    conn.commit()


#List of all possible permissions as of 3/11/23
my_perms = ['accessibilityFeatures.modify','accessibilityFeatures.read','bookmarks',
         'clipboardRead','clipboardWrite','contentSettings','debugger','declarativeNetRequest','declarativeNetRequestFeedback','desktopCapture',
         'downloads','favicon','geolocation','history','identity.email','management','nativeMessaging','notifications','pageCapture','privacy',
         'proxy','sessions','history','tabs','system.storage','tabCapture','tabGroups','topSites','ttsEngine','webAuthenticationProxy','webNavigation',
         'storage','activeTab','alarms','idle','unlimitedStorage','offscreen','scripting','declarativeNetRequestWithHostAccess','identity',
         'webRequest','webRequestBlocking','contextMenus','browsingData','background','power','contextMenus','declarativeContent','tts',
         'cookies','commands','gcm','chrome://favicon/','fileBrowserHandler','sidePanel','system.display','fontSettings', 
         'search', 'windows', 'downloads.shelf', 'system.memory', 'system.cpu', 'downloads.open',
         'None']

#https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/permissions

mozilla_perms = ['activeTab', 'alarms','background','bookmarks','browserSettings','browsingData','captivePortal',
         'clipboardRead','clipboardWrite','contentSettings','contextMenus','contextualIdentities','cookies',
         'debugger','declarativeNetRequest','declarativeNetRequestFeedback','declarativeNetRequestWithHostAccess',
         'devtools','dns','downloads','downloads.open','find','geolocation','history','identity','idle',
         'management','menus','menus.overrideContext','nativeMessaging','notifications','pageCapture','pkcs11',
         'privacy','proxy','scripting','search','sessions','storage','tabHide','tabs','theme','topSites',
         'unlimitedStorage','webNavigation','webRequest','webRequestAuthProvider','webRequestBlocking',
         'webRequestFilterResponse','webRequestFilterResponse.serviceWorkerScript']

set1 = set(my_perms)
set2 = set(mozilla_perms)

# Combine sets using union operator
combined_unique = set1.union(set2)

# Convert the set back to a list (optional)
perms = list(combined_unique)

no_perms = len(perms)

parser = argparse.ArgumentParser("Get manifest from extension")
parser.add_argument("sql", help="Input the name of the sql file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
sql_file = args.sql
verbose = args.verbose

current_dir = os.getcwd()
sql_name = os.path.basename(sql_file).split(".")[0]

#Check if csv file exists
sql_file = os.path.join(current_dir,sql_file)
if(os.path.isfile(sql_file)):
    print("File %s exists, starting to get manifests" %(sql_name))
else:
    print("File %s doesn't exists, stopping" %(sql_file))
    sys.exit()

all_files = os.path.join(current_dir,"extensions")
category_folder = os.path.join(all_files, sql_name)
create_directory(category_folder)
dir = os.path.join(category_folder,"preprocessed")

conn = create_connection(sql_file)
files = select_column(conn, 'file')
create_table_from_list(conn, perms)

no_files = len(files)
hosts = {}
optional_hosts = {}
with tqdm(total=no_files) as pbar:
    for filename in files:
        filename = filename.replace(".crx","")
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
                    optional_host_permissions = data["optional_host_permissions"]
                except:
                    optional_host_permissions = ['None']

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
            if p in perms:
                permission_list[perms.index(p)] = 1
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

        for h in optional_host_permissions:
            if h != 'None':
                if h in hosts:
                    optional_hosts[h] += 1
                else:
                    optional_hosts[h] = 1

        if verbose:
            tqdm.write(str(permission_list))

        insert_list(conn, filename, perms, permission_list)

        pbar.update(1)

if verbose:
    print(hosts)
    print(optional_hosts)

#Sort hosts
hosts = sort_dic(hosts)
optional_hosts = sort_dic(optional_hosts)

sql = """CREATE TABLE IF NOT EXISTS hosts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
number INTEGER,
optional INTEGER
);"""

create_table(conn, sql)

sql = """INSERT INTO hosts (name, number, optional) VALUES (?,?,?);"""

for host in hosts:
    insert_data(conn,sql, [host, hosts[host], 0])

for host in optional_hosts:
     insert_data(conn,sql, [host, optional_hosts[host], 1])

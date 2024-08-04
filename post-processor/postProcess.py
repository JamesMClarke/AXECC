"""
File to compare urls found while running extentions and tracker lists
https://github.com/epitron/mitm-adblock/blob/master/adblock.py
"""
from adblockparser import AdblockRules, AdblockRule
from glob import glob
import urllib.request
import csv, argparse, os, sys, time, requests, json, sqlite3, subprocess, shutil
from tqdm import tqdm
import pandas as pd

# Get the current directory path
current_dir = os.path.dirname(__file__)

# Get the parent directory path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

import common

def get_vv8_postprocessor():
    #Get list of extension dir names
  files = common.select_column(conn, 'file')
  #Set dir of crawl
  crawl_dir = os.path.join(os.path.dirname(sqlite_filepath), 'crawl')

  #Copy idldata.json from crawls for vv8 post processor
  shutil.copyfile(os.path.join(os.path.dirname(sqlite_filepath),'crawl', 'idldata.json'), os.path.join(cwd,'idldata.json'))

  #Create table for trackers identified by VV8
  sql = """ CREATE TABLE IF NOT EXISTS vv8Trackers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  extension TEXT,
  firstOrigin TEXT,
  url TEXT
  );"""

  common.create_table(conn, sql)

  #Create table list of scripts, if they are first or third party and if vv8 thinks they are trackers
  sql = """ CREATE TABLE IF NOT EXISTS firstPartyThirdParty (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  extension TEXT,
  firstOrigin TEXT,
  scriptProperty TEXT,
  thirdParty Boolean,
  tracking INTERGER,
  url TEXT
  );"""

  common.create_table(conn, sql)

  #Create table for logging calls and argements
  sql = """ CREATE TABLE IF NOT EXISTS callargs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  extension TEXT,
  apiName TEXT,
  passedArgs TEXT,
  scriptHash TEXT,
  scriptOffset TEXT,
  securityOrigin TEXT
  );"""

  common.create_table(conn,sql)

  sql_insert_vv8_tracker = '''INSERT INTO firstPartyThirdParty (extension, firstOrigin, scriptProperty, thirdParty, tracking, url) VALUES (?,?,?,?,?,?);'''
  sql_insert_fptp = '''INSERT INTO vv8Trackers  (extension, firstOrigin, url) VALUES (?,?,?);'''
  sql_insert_callargs = '''INSERT INTO callargs (extension, apiName, passedArgs, scriptHash, scriptOffset, securityOrigin) VALUES (?,?,?,?,?,?)'''

  for file_name in files:
    #try:
    vv8_logs = os.path.join(crawl_dir, file_name, 'vv8*.log')
    command = f"./vv8-post-processor -aggs adblock+fptp+callargs {vv8_logs}"
    print(command)
    try:
      result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    except:
      output_list = ""

    output_list = result.stdout.splitlines()
    for output in output_list:
      try:
        data_list = json.loads(output)

        if data_list[0] == 'firstpartythirdparty':
          print("first party third party")
          data = data_list[1]
          print(f"First Origin {data['FirstOrigin']}, Script Property {data['ScriptProperty']}, Third Party {data['ThirdParty']}, Tracking {data['Tracking']}, URL {data['URL']}")
          common.insert_data(conn, sql_insert_vv8_tracker, [file_name, data['FirstOrigin'], data['ScriptProperty'], data['ThirdParty'], data['Tracking'], data['URL']])
        elif data_list[0] == 'adblock':
          print("Adblock")
          data = data_list[1]
          print(f"Should be blocked {data['Blocked']}, First Origin {data['FirstOrigin']}, url {data['URL']}")
          common.insert_data(conn, sql_insert_fptp, [file_name, data['FirstOrigin'], data["URL"]])
        elif data_list[0] == 'callargs':
          print("Callargs")
          data = data_list[1]
          print(data)
          common.insert_data(conn, sql_insert_callargs, [file_name, data['api_name'], str(data['passed_args']), data['script_hash'], data['script_offset'], data['security_origin']])
      except:
        print(f"Error parsing: {output}")
        data_list = ["","",""]

class rule:
  def __init__(self, name, rules):
    self.name = name
    self.rules = rules

def download_rules(name, url):
  response_API = requests.get(url)
  data = response_API.text
  parse_json = json.loads(data)
  for i in parse_json:
    filename =  blocklists_dir + name + "_"+ i['name']
    urllib.request.urlretrieve(i['download_url'], filename)

def combined(filename):
  '''
  Open and combine many files into a single generator which returns all
  of their lines. (Like running "cat" on a bunch of files.)
  '''
  with open(filename) as file:
    for line in file:
      yield line

def load_rules(blocklists=None):
    rules = AdblockRules(
        combined(blocklists),
        use_re2=False,
        max_mem=1024*1024*1024
        # supported_options=['script', 'domain', 'image', 'stylesheet', 'object']
    )

    return rules

def download_and_load_lists():
    """
    Function to download and load all lists
    :return: A list of rules which have been loaded
    """

    common.create_directory(blocklists_dir)

    if not skip_download:
      #Clear dir
      files = glob(blocklists_dir+"*")
      for f in files:
        os.remove(f)


    """
    Need to download;
    EasyPrivacy (https://easylist.to/easylist/easyprivacy.txt)
    AdGuard’s Tracking Protection Filter (https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_3_Spyware/filter.txt) https://github.com/AdguardTeam/AdguardFilters/tree/master/SpywareFilter/sections
    Easy list without adult filter (https://easylist-downloads.adblockplus.org/easylist_noadult.txt)
    AdGuard’s Base Filter
    AdGuard’s Mobile ads filter (https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_11_Mobile/filter.txt)"""

    if not skip_download:
        print("Downloading tracker lists")
        #https://api.github.com/repos/AdguardTeam/AdguardFilters/contents/BaseFilter/sections
        #Download AdGuard
        download_rules("AdGuard_base", "https://api.github.com/repositories/22637619/contents/BaseFilter/sections")
        download_rules("AdGuard_Tracking", "https://api.github.com/repositories/22637619/contents/SpywareFilter/sections")
        download_rules("AdGuard_Mobile", "https://api.github.com/repositories/22637619/contents/MobileFilter/sections")

        #Download EasyList
        #https://api.github.com/repos/easylist/easylist/contents/easyprivacy
        download_rules("EasyPrivacy", "https://api.github.com/repos/easylist/easylist/contents/easyprivacy")
        download_rules("EasyList_without_adult", "https://api.github.com/repos/easylist/easylist/contents/easylist")

    blocklists = glob(blocklists_dir+"*")

    rule_list = []
    if len(blocklists) == 0:
      print("Error, no blocklists found in 'blocklists/'. Please run the 'update-blocklists' script.")
      raise SystemExit

    else:
      print("* Loading blocklists:")
      for list in blocklists:
        print("  |_ %s" % list)
        try:
          rule_list.append(rule(list.split('/')[1].split('.')[0], load_rules(list)))
        except:
          print(f"Error loading list {list}")

      print("Done loading lists, reading to check requests")
    return rule_list



def identify_network_trackers():
    """
    Function to identify network trackers
    :return: A dataframe with the extension name, url and type of any trackers
    """
    rule_list = download_and_load_lists()

    total = 0


    #Get all requests
    rows = common.select_all(conn, "requests")

    trackers = pd.DataFrame(columns=['name', 'url', 'network_tracker', 'network_tracker_type'])

    with tqdm(total=len(rows)) as pbar:
      for row in rows:
        url = row[1]
        name = row[2]
        should_block = False
        category = ""

        for rules in rule_list:
          #Checks if url should be blocked
          if rules.rules.should_block(url):
            should_block = True
            total += 1
            if len(category) == 0:
              category += rules.name
            else:
              category += ',' + rules.name

        #Write results back to db
        row = {'name':name,'url':url,'network_tracker':should_block,'network_tracker_type':category}
        trackers.loc[len(trackers)] = row
        pbar.update(1)


    print("The total number of trackers found was %s" %(total))
    return trackers

def merge_trackers(network, vv8):
    """
    Function to merge two dataframes
    :parma network: df of network trackers
    :parma vv8: df of vv8 trackers
    :return: merged df
    """
    network = network.rename(columns={'name': 'extension'})
    network = network[network['network_tracker'] == 1 ]
    network = network.drop(columns=network.columns.difference(['extension','url']))
    network['type'] = 'network'

    vv8 = vv8.drop(columns=vv8.columns.difference(['extension','url']))
    vv8['url'] = vv8['url'].str.replace('https://', '', regex=True)
    vv8['type'] = 'vv8'

    merged_df = pd.concat([network, vv8], ignore_index=True)
    return merged_df

#Get args
parser = argparse.ArgumentParser("Check sqlite file for trackers")
parser.add_argument("sqlite", help="Input the location of the sqlite file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
parser.add_argument("-s",'--skip_download', action='store_true', help="Skip downloading tracker lists")
args = parser.parse_args()
sqlite_file = args.sqlite
verbose = args.verbose
skip_download = args.skip_download

blocklists_dir = "tracker_lists/"
#Check file exists
cwd = os.getcwd()
sqlite_filepath = os.path.join(cwd, sqlite_file)
if(os.path.isfile(sqlite_filepath)):
    print("File %s exists, starting preprocessing" %(sqlite_filepath))
    conn = common.create_connection(sqlite_filepath)

else:
    print("File %s doesn't exists, stopping" %(sqlite_filepath))
    sys.exit()

conn = common.create_connection(sqlite_filepath)

get_vv8_postprocessor()

network_trackers = identify_network_trackers()
network_trackers.to_sql('network_trackers', conn)
#network_trackers = pd.read_sql_query(f"SELECT * FROM network_trackers", conn)
vv8_trackers = pd.read_sql_query(f"SELECT * FROM vv8Trackers", conn)

merged_trackers = merge_trackers(network_trackers, vv8_trackers)
merged_trackers.to_sql('tracker_summary', conn)

conn.close()

"""
File to compare urls found while running extentions and tracker lists
https://github.com/epitron/mitm-adblock/blob/master/adblock.py
"""
from adblockparser import AdblockRules, AdblockRule
from glob import glob
import urllib.request
import csv, argparse, re2, os, sys, common, time, requests, json
from tqdm import tqdm

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
        use_re2=True,
        max_mem=1024*1024*1024
        # supported_options=['script', 'domain', 'image', 'stylesheet', 'object']
    )

    return rules

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
common.create_directory(blocklists_dir)

if not skip_download:
  #Clear dir
  files = glob(blocklists_dir+"*")
  for f in files:
    os.remove(f)

#Check file exists
cwd = os.getcwd()
sqlite_filepath = os.path.join(cwd, sqlite_file)
if(os.path.isfile(sqlite_filepath)):
    print("File %s exists, starting preprocessing" %(sqlite_filepath))
else:
    print("File %s doesn't exists, stopping" %(sqlite_filepath))
    sys.exit()

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

#Sypware need the "General javascript, CSS and HTML extensions" section removing
#Base need to remove the "antiadblock" and "css_extended" sections

rule_list = []

if len(blocklists) == 0:
  print("Error, no blocklists found in 'blocklists/'. Please run the 'update-blocklists' script.")
  raise SystemExit

else:
  print("* Loading blocklists:")
  for list in blocklists:
    print("  |_ %s" % list)
    try:
      rule_list.append(rule(list, load_rules(list)))
    except:
      print(f"Error loading list {list}")

print("")
print("* Done! Proxy server is ready to go!")

total = 0
conn = common.create_connection(sqlite_filepath)
rows = common.select_all(conn, "trackers")
conn.close()
with tqdm(total=len(rows)) as pbar:
  for row in rows:
    url = row[2]
    id = row[0]
    should_block = False
    category = ""
    
    for rules in rule_list:
      #Checks if url should be blocked
      if rules.rules.should_block(url):
        should_block = True
        total += 1
        category += rules.name

    #Write results back to db
    if should_block:
      sql = ''' UPDATE trackers
            SET is_tracker = ?,
            tracker_type = ?
            WHERE id = ?'''
      conn = common.create_connection(sqlite_filepath)
      common.insert_data(conn, sql, (should_block, category, id))
      conn.close()
    else:
      sql = ''' UPDATE trackers
            SET is_tracker = ?
            WHERE id = ?'''
      conn = common.create_connection(sqlite_filepath)
      common.insert_data(conn, sql, (should_block, id))
      conn.close()
    pbar.update(1)


print("The total number of trackers found was %s" %(total))
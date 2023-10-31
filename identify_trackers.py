"""
File to compare urls found while running extentions and tracker lists
https://github.com/epitron/mitm-adblock/blob/master/adblock.py
TODO: Need to visualise the results
TODO: Need to get the latest version of tracker lists on each run
TODO: Might add a loading bar since it takes a while
"""
import os
import re2
from adblockparser import AdblockRules, AdblockRule
from glob import glob
import urllib.request
import csv

blocklists_dir = "tracker_lists/"

def download_rules(rules):
  for rule in rules:
    url = 'https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/'+rule
    filename = blocklists_dir + rule

    urllib.request.urlretrieve(url, filename)

def check_rules(filenames):
   for filename in filenames:
    with open(filename) as file:
      for line in file:
        AdblockRule(line)
        print(line)


def log(msg):
    print(msg)

def combined(filenames):
  '''
  Open and combine many files into a single generator which returns all
  of their lines. (Like running "cat" on a bunch of files.)
  '''
  for filename in filenames:
    with open(filename) as file:
      for line in file:
        yield line

def load_rules(blocklists=None):
    # TODO: Fix loading of spyware and base
    rules = AdblockRules(
        combined(blocklists),
        use_re2=True,
        max_mem=512*1024*1024
        # supported_options=['script', 'domain', 'image', 'stylesheet', 'object']
    )

    return rules

#https://github.com/AdguardTeam/AdguardFilters/tree/master/BaseFilter/sections
#baseFilters = ["adservers.txt", "adservers_firstparty.txt", "allowlist.txt", "allowlist_stealth.txt", "antiadblock.txt","banner_sizes.txt","cname_adservers.txt","content_blocker.txt","cryptominers.txt","css_extended.txt","foreign.txt","general_elemhide.txt","general_extensions.txt","general_url.txt","replace.txt","specific.txt"]
baseFilters = ["adservers.txt", "adservers_firstparty.txt",  "allowlist.txt", "allowlist_stealth.txt", "banner_sizes.txt", "cname_adservers.txt","content_blocker.txt","cryptominers.txt","foreign.txt","general_elemhide.txt","general_url.txt","replace.txt","specific.txt"]
download_rules(baseFilters)

blocklists = glob(blocklists_dir+"*")

"""
Sypware need the "General javascript, CSS and HTML extensions" section removing
Base need to remove the "antiadblock" and "css_extended" sections
"""

if len(blocklists) == 0:
  log("Error, no blocklists found in 'blocklists/'. Please run the 'update-blocklists' script.")
  raise SystemExit

else:
  log("* Available blocklists:")
  for list in blocklists:
    log("  |_ %s" % list)

log("* Loading blocklists...")
rules = load_rules(blocklists)
log("")
log("* Done! Proxy server is ready to go!")

total = 0

for log in open(os.path.join("logfile.log"), "r"):
    if "Request" not in log:
      extention = log[:-5]
      print(extention)
    #If log does not start with 'Request: '  then make that the extention name elif do the other stuff
    elif "Request: localhost/shutdown"  not in log and "Request: accounts.google.com/ListAccounts?gpsia=1&source=ChromiumBrowser&json=standard" not in log and "Request: www.googleapis.com/chromewebstore/v1.1/items/verify" not in log:
       if rules.should_block(log.replace('Request: ', '')):
        tracker = log.replace('Request: ', '')
        total += 1
        trackers = open('trackers.csv', 'a', encoding='utf-8')
        trackers.write(extention+ "," + tracker[:-1]+"\n")
        print(extention+ "," + tracker[:-1])
        trackers.close()

print("The total number of trackers found was %s" %(total))
trackers = open('trackers.csv', 'a', encoding='utf-8')
trackers.write("The total number of trackers found was %s" %(total))
trackers.close()
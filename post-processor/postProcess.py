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
from concurrent.futures import ProcessPoolExecutor, as_completed

# Get the current directory path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
import common

class rule:
    def __init__(self, name, filepath, rules):
        self.name = name
        self.filepath = filepath
        self.rules = rules

def get_vv8_postprocessor():
    files = common.select_column(conn, 'file')
    crawl_dir = os.path.join(os.path.dirname(sqlite_filepath), 'crawl')
    shutil.copyfile(os.path.join(os.path.dirname(sqlite_filepath), 'crawl', 'idldata.json'), os.path.join(cwd, 'idldata.json'))

    common.create_table(conn, """
    CREATE TABLE IF NOT EXISTS vv8Trackers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      extension TEXT,
      firstOrigin TEXT,
      url TEXT
    );""")

    common.create_table(conn, """
    CREATE TABLE IF NOT EXISTS firstPartyThirdParty (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      extension TEXT,
      firstOrigin TEXT,
      scriptProperty TEXT,
      thirdParty Boolean,
      tracking INTERGER,
      url TEXT
    );""")

    common.create_table(conn, """
    CREATE TABLE IF NOT EXISTS callargs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      extension TEXT,
      apiName TEXT,
      passedArgs TEXT,
      scriptHash TEXT,
      scriptOffset TEXT,
      securityOrigin TEXT
    );""")

    sql_insert_vv8_tracker = '''INSERT INTO vv8Trackers (extension, firstOrigin, url) VALUES (?,?,?)'''
    sql_insert_fptp = '''INSERT INTO firstPartyThirdParty (extension, firstOrigin, scriptProperty, thirdParty, tracking, url) VALUES (?,?,?,?,?,?)'''
    sql_insert_callargs = '''INSERT INTO callargs (extension, apiName, passedArgs, scriptHash, scriptOffset, securityOrigin) VALUES (?,?,?,?,?,?)'''

    batch_size = 1000
    batch_vv8_tracker, batch_fptp, batch_callargs = [], [], []

    def process_file(file_name):
        vv8_logs = os.path.join(crawl_dir, file_name, 'vv8*.log')
        command = f"./vv8-post-processor -aggs adblock+fptp+callargs {vv8_logs}"

        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            output_list = result.stdout.splitlines()

            for output in output_list:
                try:
                    data_list = json.loads(output)
                    if data_list[0] == 'firstpartythirdparty':
                        data = data_list[1]
                        batch_fptp.append([file_name, data['FirstOrigin'], data['ScriptProperty'], data['ThirdParty'], data['Tracking'], data['URL']])
                    elif data_list[0] == 'adblock':
                        data = data_list[1]
                        batch_vv8_tracker.append([file_name, data['FirstOrigin'], data['URL']])
                        with open(os.path.join('vv8Trackers.csv'), 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([file_name, data['FirstOrigin'], data['URL']])
                    elif data_list[0] == 'callargs':
                        data = data_list[1]
                        batch_callargs.append([file_name, data['api_name'], str(data['passed_args']), data['script_hash'], data['script_offset'], data['security_origin']])

                    if len(batch_vv8_tracker) >= batch_size:
                        common.insert_many(conn, sql_insert_vv8_tracker, batch_vv8_tracker)
                        batch_vv8_tracker.clear()
                    if len(batch_fptp) >= batch_size:
                        common.insert_many(conn, sql_insert_fptp, batch_fptp)
                        batch_fptp.clear()
                    if len(batch_callargs) >= batch_size:
                        common.insert_many(conn, sql_insert_callargs, batch_callargs)
                        batch_callargs.clear()

                except:
                    print(f"Error parsing: {output}")
        except:
            return

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        executor.map(process_file, files)

    if batch_vv8_tracker:
        common.insert_many(conn, sql_insert_vv8_tracker, batch_vv8_tracker)
    if batch_fptp:
        common.insert_many(conn, sql_insert_fptp, batch_fptp)
    if batch_callargs:
        common.insert_many(conn, sql_insert_callargs, batch_callargs)

def download_rules(name, url):
    response_API = requests.get(url)
    data = response_API.text
    parse_json = json.loads(data)
    for i in parse_json:
        filename = blocklists_dir + name + "_" + i['name']
        urllib.request.urlretrieve(i['download_url'], filename)

def combined(filename):
    with open(filename) as file:
        for line in file:
            yield line

def load_rules(blocklists=None):
    rules = AdblockRules(
        combined(blocklists),
        use_re2=False,
        max_mem=1024*1024*1024
    )
    return rules

def download_and_load_lists():
    common.create_directory(blocklists_dir)

    if not skip_download:
        files = glob(blocklists_dir + "*")
        for f in files:
            os.remove(f)

        print("Downloading tracker lists")
        download_rules("AdGuard_base", "https://api.github.com/repositories/22637619/contents/BaseFilter/sections")
        download_rules("AdGuard_Tracking", "https://api.github.com/repositories/22637619/contents/SpywareFilter/sections")
        download_rules("AdGuard_Mobile", "https://api.github.com/repositories/22637619/contents/MobileFilter/sections")
        download_rules("EasyPrivacy", "https://api.github.com/repos/easylist/easylist/contents/easyprivacy")
        download_rules("EasyList_without_adult", "https://api.github.com/repos/easylist/easylist/contents/easylist")

    blocklists = glob(blocklists_dir + "*")

    rule_list = []
    if len(blocklists) == 0:
        print("Error, no blocklists found in 'tracker_lists/'. Please run the 'update-blocklists' script.")
        raise SystemExit
    else:
        print("* Loading blocklists:")
        for list_path in blocklists:
            print("  |_ %s" % list_path)
            try:
                filename = os.path.basename(list_path).split('.')[0]
                rule_list.append(rule(filename, list_path, load_rules(list_path)))
            except Exception as e:
                print(f"Error loading list {list_path}: {e}")

        print("Done loading lists, ready to check requests")
    return rule_list

def extract_rule_lines(rule_list):
    rule_lines = []
    for r in rule_list:
        with open(r.filepath, 'r') as f:
            rule_lines.extend(f.readlines())
    return rule_lines

def rebuild_rules(raw_lines):
    return AdblockRules(raw_lines, use_re2=False)

def process_batch(batch, raw_lines):
    rules = rebuild_rules(raw_lines)
    results = []
    for row in batch:
        url = row[1]
        name = row[2]
        should_block = rules.should_block(url)
        results.append({
            'name': name,
            'url': url,
            'network_tracker': should_block,
            'network_tracker_type': 'tracker' if should_block else ''
        })
    return results

def identify_network_trackers():
    rule_list = download_and_load_lists()
    raw_lines = extract_rule_lines(rule_list)

    rows = common.select_all(conn, "requests")
    batch_size = 10000
    batches = [rows[i:i + batch_size] for i in range(0, len(rows), batch_size)]

    trackers_data = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_batch, batch, raw_lines) for batch in batches]
        with tqdm(total=len(rows)) as pbar:
            for future in as_completed(futures):
                result = future.result()
                trackers_data.extend(result)
                pbar.update(len(result))

    return pd.DataFrame(trackers_data)

def merge_trackers(network, vv8):
    network = network.rename(columns={'name': 'extension'})
    network = network[network['network_tracker'] == 1]
    network = network.drop(columns=network.columns.difference(['extension', 'url']))
    network['type'] = 'network'

    vv8 = vv8.drop(columns=vv8.columns.difference(['extension', 'url']))
    vv8['url'] = vv8['url'].str.replace('https://', '', regex=True)
    vv8['type'] = 'vv8'

    merged_df = pd.concat([network, vv8], ignore_index=True)
    return merged_df

#Get args
parser = argparse.ArgumentParser("Check sqlite file for trackers")
parser.add_argument("sqlite", help="Input the location of the sqlite file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
parser.add_argument("-s",'--skip_download', action='store_true', help="Skip downloading tracker lists")
parser.add_argument("--network", action='store_false', default='true', help="Only detect network trackers")
parser.add_argument("--vv8", action='store_false', default='true', help="Only detect vv8 trackers")
args = parser.parse_args()
sqlite_file = args.sqlite
verbose = args.verbose
skip_download = args.skip_download
only_network = args.network
only_vv8 = args.vv8
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

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # optional, mostly needed for Windows .exe packaging
    # Your other code can follow here

    if only_network:
        print("Processing vv8 post processor")
        get_vv8_postprocessor()

    if only_vv8:
      network_trackers = identify_network_trackers()
      network_trackers.to_sql('network_trackers', conn)
      #network_trackers = pd.read_sql_query(f"SELECT * FROM network_trackers", conn)
      vv8_trackers = pd.read_sql_query(f"SELECT * FROM vv8Trackers", conn)

    if only_network and only_vv8:
      print("Merging network and vv8 trackers")
      merged_trackers = merge_trackers(network_trackers, vv8_trackers)
      merged_trackers.to_sql('tracker_summary', conn)

    conn.close()

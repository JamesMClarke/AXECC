"""
This file looks at the manifests and finds which hosts are inside the permissions
"""
import os, json, re, csv
import pandas as pd

Perms = ['accessibilityFeatures.modify','accessibilityFeatures.read','bookmarks',
         'clipboardRead','clipboardWrite','contentSettings','debugger','declarativeNetRequest','declarativeNetRequestFeedback','desktopCapture',
         'downloads','favicon','geolocation','history','identity.email','management','nativeMessaging','notifications','pageCapture','privacy',
         'proxy','sessions','history','tabs','system.storage','tabCapture','tabGroups','topSites','ttsEngine','webAuthenticationProxy','webNavigation',
         'storage','activeTab','alarms','idle','unlimitedStorage','offscreen','scripting','declarativeNetRequestWithHostAccess','identity',
         'webRequest','webRequestBlocking','contextMenus','browsingData','background','power','contextMenus','declarativeContent','tts',
         'cookies','commands','gcm','chrome://favicon/','fileBrowserHandler','sidePanel','system.display','fontSettings',
         'None']

def sort_dic(dic):
    return dict(sorted(dic.items(), key=lambda item: item[1], reverse=True))

def count_hosts(csv_file, dir):
    host = {}
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        for row in rows:
            filename = row[7]
            try:
                with open( os.path.join(dir, str(filename.split('.')[0]), 'manifest.json')) as f:
                    data = json.load(f)
                    try:
                        permissions = data["permissions"]
                    except:
                        permissions = ['None']

                    try:
                        host_permissions = data["host_permissions"]
                    except:
                        host_permissions = ['None']
                
                for p in permissions:
                    if p not in Perms and p != 'None':
                        if p in host:
                            host[p] += 1
                        else:
                            host[p] = 1

                for h in host_permissions:
                    if h != 'None':
                        if h in host:
                            host[h] += 1
                        else:
                            host[h] = 1
            except:
                errors_file = open('Error Hosts.txt', 'a', encoding='utf-8')
                errors_file.write(filename+'\n')
                errors_file.close()
    return host

def combine_dic(one, two):
    total = {}
    for key in one:
        if key in total:
            total[key] += one[key]
        else:
            total[key] = one[key]
    
    for key in two:
        if key in total:
            total[key] += two[key]
        else:
            total[key] = two[key]
    return total

def make_table(screen_reader, accessibility):
    total = sort_dic(combine_dic(screen_reader, accessibility))
        
    table = """
    \\begin{table}[h]
    \centering
    \\begin{tabular}{lccc} \\toprule
        Permission & Accessibility & Screen Reader & Total \\\\ \midrule
    """
    for key, value in total.items():
        if value == 2:
            break
        
        #Make sure that they key is in both dics
        if key not in accessibility:
            accessibility[key] = 0
        if key not in screen_reader:
            screen_reader[key] = 0

        table += """%s & %s & %s & %s\\\\\n""" %(key, accessibility[key], screen_reader[key], value)
    
    table += """
    \\bottomrule
    \end{tabular}
    \caption{List of hosts in the permissions within the manifest file with 3 or more extentions}
    \label{tab:hosts}
    \end{table}
    """

    return table

screen_reader = count_hosts("screen_reader.csv", 'screen_reader_unzipped')
accessibility = count_hosts("accessibility.csv", "accessibility_unzipped")

print(make_table(screen_reader, accessibility))
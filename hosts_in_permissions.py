"""
This file looks at the manifests and finds which hosts are inside the permissions
"""
import os, json, re, csv
import pandas as pd

print('running')

screen_reader = 'screen_reader_unzipped'
accessibility = 'accessibility_unzipped'

Perms = ['accessibilityFeatures.modify','accessibilityFeatures.read','bookmarks',
         'clipboardRead','clipboardWrite','contentSettings','debugger','declarativeNetRequest','declarativeNetRequestFeedback','desktopCapture',
         'downloads','favicon','geolocation','history','identity.email','management','nativeMessaging','notifications','pageCapture','privacy',
         'proxy','sessions','history','tabs','system.storage','tabCapture','tabGroups','topSites','ttsEngine','webAuthenticationProxy','webNavigation',
         'storage','activeTab','alarms','idle','unlimitedStorage','offscreen','scripting','declarativeNetRequestWithHostAccess','identity',
         'webRequest','webRequestBlocking','contextMenus','browsingData','background','power','contextMenus','declarativeContent','tts',
         'cookies','commands','gcm','chrome://favicon/','fileBrowserHandler','sidePanel','system.display','fontSettings',
         'None']

screen_reader_host = {}
accessibility_host = {}

with open('screen_reader.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    for row in rows:
        filename = row[7]
        try:
            with open( os.path.join(screen_reader, str(filename.split('.')[0]), 'manifest.json')) as f:
                data = json.load(f)
                try:
                    permissions = data["permissions"]
                except:
                    permissions = ['None']
            
            for p in permissions:
                if p not in Perms:
                    if p in screen_reader_host:
                        screen_reader_host[p] += 1
                    else:
                        screen_reader_host[p] = 1


        except:
            errors_file = open('Error Hosts.txt', 'a', encoding='utf-8')
            errors_file.write(filename+'\n')
            errors_file.close()

with open('accessibility.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    for row in rows:
        filename = row[7]
        try:
            with open( os.path.join(accessibility, str(filename.split('.')[0]), 'manifest.json')) as f:
                data = json.load(f)
                try:
                    permissions = data["permissions"]
                except:
                    permissions = ['None']
            
            for p in permissions:
                if p not in Perms:
                    if p in accessibility_host:
                        accessibility_host[p] += 1
                    else:
                        accessibility_host[p] = 1


        except:
            errors_file = open('Error Hosts.txt', 'a', encoding='utf-8')
            errors_file.write(filename+'\n')
            errors_file.close()

#print(dict(sorted(screen_reader_host.items(), key=lambda item: item[1])))
#print(dict(sorted(accessibility_host.items(), key=lambda item: item[1])))

df = pd.DataFrame([screen_reader_host, accessibility_host])
#df.sort_values(inplace=True)

print(df)

df_transposed = df.transpose()
df_transposed.sort_values(by=0,inplace=True)
print(df_transposed)

df_transposed.to_csv('Hosts_in_permissions.csv', index=True, header=True)

"""for row in df_transposed:
    print(row)

hosts_file = open('Hosts in permissions.txt', 'a', encoding='utf-8')
hosts_file.write(df_transposed+'\n')
hosts_file.close()
"""
#TODO Finish this script to view manifest file, and put into a csv
import os, json, re, csv

print('running')

dir = 'accessibility_unzipped'

Perms = ['http://*/*','https://*/*','*://*/*','<all_urls>','accessibilityFeatures.modify','accessibilityFeatures.read','bookmarks',
         'clipboardRead','clipboardWrite','contentSettings','debugger','declarativeNetRequest','declarativeNetRequestFeedback','desktopCapture',
         'downloads','favicon','geolocation','history','identity.email','management','nativeMessaging','notifications','pageCapture','privacy',
         'proxy','sessions','history','tabs','system.storage','tabCapture','tabGroups','topSites','ttsEngine','webAuthenticationProxy','webNavigation',
         'storage','activeTab','alarms','idle','unlimitedStorage','offscreen','scripting','declarativeNetRequestWithHostAccess','identity',
         'webRequest','webRequestBlocking','contextMenus','browsingData','background','power','contextMenus','declarativeContent','tts',
         'cookies','commands','gcm','chrome://favicon/','fileBrowserHandler','sidePanel','system.display','fontSettings',
         'None']

with open('accessibility.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    for row in rows:
        print(', '.join(row))
        filename = row[7]
        print(filename)
        try:
            with open( os.path.join(dir, str(filename.split('.')[0]), 'manifest.json')) as f:
                data = json.load(f)
                try:
                    
                    permissions = data["permissions"]
                except:
                    permissions = ['None']
            
            for p in permissions:
                if p not in Perms:
                    other_perm_file = open('OtherPermissions.txt', 'a', encoding='utf-8')
                    other_perm_file.write(p+' - '+filename)
                    print(p)
                    other_perm_file.write('\n')
                    other_perm_file.close()

            permission_list = []

            for perm in Perms:
                if perm in permissions:
                    permission_list.append('1')
                else:
                    permission_list.append('0')
            
            perm_file = open('example.csv', 'a', encoding='utf-8')
            for i in row:
                perm_file.write(i + ',')

            for p in permission_list:
                perm_file.write(p + ',')
            perm_file.write('\n')
            perm_file.close()
        except:
            errors_file = open('Error Manifest.txt', 'a', encoding='utf-8')
            errors_file.write(filename+'\n')
            errors_file.close()
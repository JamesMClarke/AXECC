"""
Merges multiple csv files into one, making sure to avoid duplicates
"""

import csv,os

with open('screen_reader.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    for row in rows:
        if(row[4] != 'Not Mentioned'):
            try:
                users = int(row[4])
            except:
                users = int(row[4][:-1])
            rating = float(row[5])
            link = row[2]
            if users >= 1000 and rating >= 3:
                print(users)
                print(rating)
                with open('all_popular.csv', 'r', newline='') as csvfile2:
                    reader2 = csv.reader(csvfile2)
                    if os.stat("all_popular.csv").st_size != 0:
                        found = False
                        for row2 in reader2:
                            if link in row2:
                                print('Value found in row:', row)
                                found = True
                            
                        if not found:
                            merge = open('all_popular.csv', 'a',  encoding='utf-8')
                            for i in row:
                                merge.write(i + ',')
                            merge.write('\n')
                            print('Written')
                            merge.close()

                    else:
                        #If file is empty add headings to top of file

                        headings = ['Name', 'URL', 'Developer', 'Category', 'Users', 'Rating', 'Rated by', 'File',
                                'http://*/*','https://*/*','*://*/*','<all_urls>','accessibilityFeatures.modify','accessibilityFeatures.read','bookmarks',
                                'clipboardRead','clipboardWrite','contentSettings','debugger','declarativeNetRequest','declarativeNetRequestFeedback','desktopCapture',
                                'downloads','favicon','geolocation','history','identity.email','management','nativeMessaging','notifications','pageCapture','privacy',
                                'proxy','sessions','history','tabs','system.storage','tabCapture','tabGroups','topSites','ttsEngine','webAuthenticationProxy','webNavigation',
                                'storage','activeTab','alarms','idle','unlimitedStorage','offscreen','scripting','declarativeNetRequestWithHostAccess','identity',
                                'webRequest','webRequestBlocking','contextMenus','browsingData','background','power','contextMenus','declarativeContent','tts',
                                'cookies','commands','gcm','chrome://favicon/','fileBrowserHandler','sidePanel','system.display','fontSettings',
                                'None']

                        merge = open('all_popular.csv', 'a', encoding='utf-8')
                        for p in headings:
                            merge.write(','+ p)
                        merge.write('\n')
                        merge.close()
""""
Simple script to get the versions of extentions
"""

"""
This file looks at the manifests and finds which hosts are inside the permissions
"""
import os, json, re, csv
import pandas as pd

screen_reader = 'screen_reader_unzipped'
accessibility = 'accessibility_unzipped'


screen_reader_host = {}
accessibility_host = {}

manifest_screen_reader = {3:0,2:0}
manifest_accessibility = {3:0,2:0}

with open('screen_reader.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    for row in rows:
        filename = row[7]
        try:
            with open( os.path.join(screen_reader, str(filename.split('.')[0]), 'manifest.json')) as f:
                data = json.load(f)
                if data['manifest_version'] == 3:
                    manifest_screen_reader[3] += 1
                elif data['manifest_version'] == 2:
                    manifest_screen_reader[2] += 1
        except:
            errors_file = open('Error Hosts.txt', 'a', encoding='utf-8')
            errors_file.write(filename+'\n')
            errors_file.close()

    print("Screen reader: %s" %(manifest_screen_reader))

with open('accessibility.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)
    for row in rows:
        filename = row[7]
        try:
            with open( os.path.join(accessibility, str(filename.split('.')[0]), 'manifest.json')) as f:
                data = json.load(f)
                if data['manifest_version'] == 3:
                    manifest_accessibility[3] += 1
                elif data['manifest_version'] == 2:
                    manifest_accessibility[2] += 1


        except:
            errors_file = open('Error Hosts.txt', 'a', encoding='utf-8')
            errors_file.write(filename+'\n')
            errors_file.close()

    print("Accessibility: %s" %(manifest_accessibility))

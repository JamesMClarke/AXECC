"""
Simple script to unzip all crx files
"""
import zipfile
import os

crx_dir = 'screen_reader_crx_files'
output_dir = 'screen_reader_unzipped'

for filename in os.listdir(crx_dir):
    try:
        with zipfile.ZipFile(os.path.join(crx_dir,filename), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(output_dir,filename.split('.')[0]))
    except:
            errors_file = open('Error Unzip.txt', 'a', encoding='utf-8')
            errors_file.write(filename+'\n')
            errors_file.close()


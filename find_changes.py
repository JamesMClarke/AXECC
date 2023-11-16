import time
import os
import pandas as pd
import difflib
import re 
from bs4 import BeautifulSoup

diff_folder = 'diffs'
html_dir = 'html_files'

df = pd.read_csv('all_popular.csv')
extensions = df['File']
extensions = extensions[:-1]

accessibility = 'accessibility_crx_files'
screen_reader = 'screen_reader_crx_files'
current_dir = os.getcwd()

baseline = open(os.path.join(html_dir,'baseline.html'), 'r').readlines()

matches = open('matches.csv', 'a', encoding='utf-8')
matches.write("File, Match, Links,Scripts,CSS,Blank,Other\n")
matches.close()

for extension in extensions:
    try:
        #Gets the code of the website and compare that against a baseline

        matches = open('matches.csv', 'a', encoding='utf-8')
        html = open(os.path.join(html_dir,extension+'.html'), 'r').readlines()

        if baseline == html:
            matches.write(extension +",Matches \n")
            print('Matches')
        else:
            data = BeautifulSoup(html, 'html.parser')
            data = data.findAll(string=True)
            no_links = 0
            no_scripts = 0
            no_css = 0
            no_blank = 0
            no_other = 0
            
            for line in html:
                link = ".*http.*"
                script = ".*script.*"
                css = "(.*[.].*{)|(.*[#].*{)|(.*:.*;)|(.*}.*)"
                #end = ".*}.*"
                blank = " *\n"
                if 'http' in line:
                    no_links += 1
                
                if 'script' in line or 'Script' in line:
                    no_scripts += 1

                if re.match(css,line):
                    no_css += 1

                elif re.match(blank, line):
                    no_blank += 1

                else:
                    #changes_file.write('Other\n')
                    no_other += 1
                    #changes_file.write(line+'\n')
                    #changes_file.close()
            """
            htmlDiffer = difflib.HtmlDiff()
            htmlDiffs = htmlDiffer.make_file(baseline, html)

            with open(os.path.join(diff_folder, extension+'.html'), 'w') as outfile:
                outfile.write(htmlDiffs)
            
            """
            matches.write("%s,Doesn't match,%i,%i,%i,%i,%i\n"%(extension,no_links,no_scripts,no_css,no_blank,no_other))
            #matches.write(extension +",Doesn't match,"\n")
            print("Doesn't match")
    except:
        errors_file = open('Error Match.txt', 'a', encoding='utf-8')
        errors_file.write(extension+'\n')
        errors_file.close()
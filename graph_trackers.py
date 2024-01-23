import argparse, os, sys, common, tldextract
from urllib.parse import urlparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import numpy as np  
graph_folder = 'tables_and_graphs'
#Get args
parser = argparse.ArgumentParser("Create tables and graphs based on the output of identify trackers")
parser.add_argument("sqlite", help="Input the location of the sqlite file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
parser.add_argument("-g",'--graphical', type=bool)
args = parser.parse_args()
sqlite_file = args.sqlite
graphical = args.graphical

if(not graphical):
    matplotlib.use("pgf")

plt.rcParams["figure.figsize"] = [6, 4]
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'Linux Libertine O',
    'font.size': 9
})
plt.rcParams['figure.constrained_layout.use'] = True

def bar_horizontal(c, title):
    sns.set_style('whitegrid')
    sns.set_palette('colorblind')
    ax = sns.barplot(x =list(c.values()), y=list(c.keys()))
    #ax.set_title(title)
    plt.xlabel(title)
    plt.ylabel("Name")
    if graphical:
            plt.show()
    else:
        plt.savefig(os.path.join(graph_folder, title + '.pgf'), bbox_inches='tight')
    matplotlib.pyplot.close()

def pie(c, title):
    data = list(c.values())
    labels = list(c.keys())
    colours = sns.color_palette("colorblind")
    fig, ax = plt.subplots()
    #ax.pie(data, labels=labels, colors=colours, autopct='%1.1f%%')

    total = 0
    for i in data:
        total += i
    plt.xlabel(title)
    #ax.pie(data, labels=[f'{l} ({s} apps)' for l, s in zip(labels, data)], colors=colours)
    plt.pie(data, labels=[f'{l} ({s} trackers)' for l, s in zip(labels, data)])
    #ax.set_title(title)
    if graphical:
            plt.show()
    else:
        plt.savefig(os.path.join(graph_folder, title + '.pgf'), bbox_inches='tight')
    matplotlib.pyplot.close()

def count_apps(apps):
    count = {}
    for app in apps:
        if app in count:
            count[app]  += 1
        else:
            count[app] = 1
    
    return(dict(sorted(count.items(), key=lambda item: item[1], reverse=True)))

def count_urls(urls):
    count = {}
    for url in urls:
        extracted = tldextract.extract(url)
        domain = extracted.domain + '.' + extracted.suffix
        if domain in count:
            count[domain]  += 1
        else:
            count[domain] = 1
    return(dict(sorted(count.items(), key=lambda item: item[1], reverse=True)))

def count_counts(counts):
    counts_of_counts = {}
    for count in counts.values():
        if count in counts_of_counts:
            counts_of_counts[count] += 1
        else:
            counts_of_counts[count] = 1
    return(dict(sorted(counts_of_counts.items(), reverse=False)))

def create_other(counts: dict, value: int):
    """
    Basic function to add other, this is done for all counts that are less than or equal to the value provided
    """
    counts_new = {}
    counts_new['Other'] = 0
    for url in counts:
        if counts[url] <= value:
            counts_new['Other'] += value
        else:
            counts_new[url] = counts[url]
    
    return counts_new

#Check file exists
cwd = os.getcwd()
sqlite_filepath = os.path.join(cwd, sqlite_file)
if(os.path.isfile(sqlite_filepath)):
    print("File %s exists, starting preprocessing" %(sqlite_filepath))
else:
    print("File %s doesn't exists, stopping" %(sqlite_filepath))
    sys.exit()

conn = common.create_connection(sqlite_filepath)
data = pd.read_sql_query('SELECT * FROM trackers WHERE is_tracker = 1', conn)
conn.close()

print(f"The total number of trackers is {len(data)}")

#TODO Work out trackers per app
#TODO Work on trackers per tld

apps = count_apps(data['extension'])
domains = count_urls(data['tracker_url'])

print(f"These trackers come from {len(apps)} extensions")
print(f"These trackers come from {len(domains)} TLDs")
domains = create_other(domains, 6)
pie(domains,"Number of trackers per domain")
#apps = create_other(apps, 5)
#bar_horizontal(apps,"Trackers per extension")


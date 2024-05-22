import argparse, os, sys, common
from urllib.parse import urlparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import numpy as np
import sqlite3


plt.rcParams["figure.figsize"] = [6, 4]
matplotlib.rcParams.update({
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

def create_summary_table(output_dir, extensions):
    """
    Function to create a summary of the extension
    :parma output_dir: where to save the resulting file
    :parma input_sqlite: filepath of the sqlite file to create a table for
    """
    #TODO Finish this
    summary_file = os.path.join(output_dir, "summary.tex")
    print(f"Creating summary at {summary_file}")

    summary_table = ""

    headings = """\\begin{table}[h]
    \\centering
    \\begin{tabular}{cccccccc} \\toprule
        \\multirow{2}{*}{Search term} & \\# & \\multirow{2}{*}{Total users} & Avg. \\#  & Avg.  & Avg. \\#  & \\multicolumn{2}{c}{Manifest} \\\\
        & Extensions & &  users & rating & Permissions & V2 & V3 \\\\ \\midrule"""

    summary_table += headings

def count_unique(df, column):
    """
    Function to count the number of times each value occurs in a column
    :parma df: Dataframe containing list of item
    :parma column: Column to count items in
    :return: Returns a dictonary of tracking extensions and number of trackers
    """
    counts = df[column].value_counts().to_dict()
    return(counts)

def create_trackers_table(trackers, extensions):
    """
    Function to create a table summarising the network trackers
    :parma trackers: Dataframe containing a summary of the trackers
    :parma extensions: Dataframe containing the extensions
    :return: Latex table containing trackers
    """

    table = ""

    table += """\\begin{table}[h]
    \\centering
    \\begin{tabular}{lcccc} \\toprule
        Extension & Total & \\# Detected & \\# only detected by & \\# only detected\\\\
         & Detected & by both & Network Analysis & by VV8 \\\\ \\midrule
"""
    for index, row in trackers.iterrows():
        mask = extensions['name'] == row['name']
        # Get value from url based on the filter
        url = extensions.loc[mask, 'url'].iloc[0]

        table += f"""       \\href{{{url}}}{{{row['name'].replace("&", "\\&")}}} & {row['total']} & {row['both']} & {row['vv8']} & {row['network']} \\\\ \n"""

    table += """        \\bottomrule
    \\end{tabular}
    \\caption{Number of trackers per extension}
    \\label{tab:trackers}
\\end{table}
    """
    return table

def create_trackers_dataframe(extensions):
    """
    Function to create a dataframe summarising the network trackers
    :parma extensions: Dataframe containing the extensions
    :return: Dataframe containing a summary of the tracks found
    """
    vv8 = pd.read_sql_query("SELECT extension, url FROM vv8Trackers", conn)
    network = pd.read_sql_query("SELECT extension, url FROM requests WHERE is_tracker = 1", conn)

    totals = pd.DataFrame(columns=['name','total','both','vv8','network'])
    for extension in extensions['file']:
        if (vv8['extension'].isin([extension]).any()) or (network['extension'].isin([extension]).any()):
            mask = vv8['extension'] == extension
            vv8_this_extension = vv8[mask]

            mask = network['extension'] == extension
            network_this_extension = network[mask]

            both = network_this_extension['url'].isin(vv8_this_extension['url']).sum()
            just_network = len(network_this_extension) - both
            just_vv8 = len(vv8_this_extension) -both
            total = just_network + just_vv8 + both

            # Boolean mask for filtering
            mask = extensions['file'] == extension
            # Get value from name based on the filter
            name = extensions.loc[mask, 'name'].iloc[0]

            #Create row
            row = {'name': name, 'total':total, 'both': both, 'vv8': just_vv8, 'network':just_network}
            totals.loc[len(totals)] = row

    #Sort dataframe
    return totals.sort_values(by='total', ascending=False)

#Get args
parser = argparse.ArgumentParser("Create tables and graphs based on sqlite file")
parser.add_argument("sqlite", help="Input the location of the sqlite file to be processed.", type=str)
parser.add_argument("-v",'--verbose', action='store_true')
parser.add_argument("-g",'--graphical', type=bool)
args = parser.parse_args()
sqlite_file = args.sqlite
graphical = args.graphical

#Check file exists
cwd = os.getcwd()
sqlite_filepath = os.path.join(cwd, sqlite_file)
if(os.path.isfile(sqlite_filepath)):
    print("File %s exists, starting to create tables and graphs" %(sqlite_filepath))
else:
    print("File %s doesn't exists, stopping" %(sqlite_filepath))
    sys.exit()

output_dir = os.path.join(os.path.dirname(sqlite_filepath), "tables_and_graphs")
common.create_directory(output_dir)

conn = sqlite3.connect(sqlite_filepath)

crawl = pd.read_sql_query("SELECT * FROM crawl", conn)
extensions = pd.read_sql_query("SELECT * FROM extensions", conn)
hosts = pd.read_sql_query("SELECT * FROM hosts", conn)
permissions = pd.read_sql_query("SELECT * FROM permissions", conn)

trackers = create_trackers_dataframe(extensions)
print(create_trackers_table(trackers, extensions))

quit()


conn = common.create_connection(sqlite_filepath)
data = pd.read_sql_query('SELECT * FROM crawl WHERE success = 1', conn)
conn.close()

#TODO Ignore baseline
print(f"The total number extensions crawed was {len(data)}")
print(type(data['lighthouse']))

# Count the occurrences of each unique item
value_counts = data['lighthouse'].value_counts()
value_counts = value_counts.sort_values(ascending=True)
# Plot the bar chart
value_counts.plot(kind="bar")

# Add labels and title (optional)
plt.xlabel("Lighthouse Score")
plt.ylabel("Number of Occurrences")
plt.title("Distribution of Values in the Series")

# Display the plot
plt.show()
#TODO Save to svg file

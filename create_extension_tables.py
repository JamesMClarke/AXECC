import common, argparse, os, sys, operator
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from matplotlib.lines import Line2D

matplotlib.use("pgf")

plt.rcParams["figure.figsize"] = [6, 4]
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'Linux Libertine O',
    'font.size': 9
})
plt.rcParams['figure.constrained_layout.use'] = True


parser = argparse.ArgumentParser("Check sqlite file for trackers")
parser.add_argument( "-f", "--folder",  help="Input the location of the folders to be processed.", type=str, action="append")
parser.add_argument("-v",'--verbose', action='store_true')
args = parser.parse_args()
csv_folders = args.folder
verbose = args.verbose

#Check file exists
cwd = os.getcwd()
for file in csv_folders:
    csv_filepath = os.path.join(cwd, file)
    if(os.path.isdir(csv_filepath)):
        print("Folder %s exists" %(csv_filepath))
    else:
        print("Folder %s doesn't exists, stopping" %(csv_filepath))
        sys.exit()

output_dir = os.path.join(cwd,"tables_and_graphs")
common.create_directory(output_dir)
summary_file = os.path.join(output_dir, "summary.tex")

print(f"Creating summary at {summary_file}")

headings = """\\begin{table}[h]
    \centering
    \\begin{tabular}{cccccccc} \\toprule
        \multirow{2}{*}{Search term} & \# & \multirow{2}{*}{Total users} & Avg. \#  & Avg.  & Avg. \#  & \multicolumn{2}{c}{Manifest} \\\\ 
        & Extensions & &  users & rating & Permissions & V2 & V3 \\\\ \midrule"""

#Create summary of permissions and info
with open(summary_file, 'w') as f:
    f.write(headings)

    for file in csv_folders:
        file = os.path.join(file,"permissions_and_info.csv")
        csv_filepath = os.path.join(cwd, file)
        df = pd.read_csv(csv_filepath)
        df.drop(columns=['None'], inplace=True)
        total_ext = len(df['Name'])
        df[' population'] = df[' population'].str.replace('+', '')
        df[' population'] = df[' population'].str.replace('Not Mentioned', '0')
        total_population = round(df[' population'].astype(float).sum())
        average_population = round(total_population / total_ext)
        average_rating = round(df[' rating'].astype(float).sum() / total_ext)
        df['total_perms']= df.iloc[:,9:-1].astype(float).sum(axis=1)
        total_perms = df['total_perms'].sum()
        average_perms = round(total_perms/total_ext)

        #TODO Fix this
        #For some reason some are text and some are ints
        v2_count = len(df[(df[' manifest_version']==2)])
        v3_count = len(df[(df[' manifest_version']==3)])
        v2_count += len(df[(df[' manifest_version']=="2")])
        v3_count += len(df[(df[' manifest_version']=='3')])

        txt = f"""    
        {os.path.dirname(file).split('/')[-1].replace("_", " ").capitalize()} & {total_ext} & {total_population} & {average_population} & {average_rating} & {average_perms} & {v2_count} & {v3_count} \\\\"""
        f.write(txt)
    
    txt = """ \\bottomrule
    \end{tabular}
    \caption{Information on each of our search terms categories.}
    \label{tab:extension_overview}
\end{table}"""
    f.write(txt)
    f.close()

count_hosts = {}

individual_hosts = []

names = []

#Generates long host file for each category
for file in csv_folders:
    file = os.path.join(file,"hosts.csv")
    csv_filepath = os.path.join(cwd, file)
    df = pd.read_csv(csv_filepath)
    total_host = len(df.values[0])
    file_name = os.path.dirname(file).split('/')[-1]
    host_file = os.path.join(output_dir, file_name+"_host.tex")
    hosts = {}
    names.append(os.path.dirname(file).split('/')[-1].replace("_", " ").capitalize())
    print(f"Creating host table at {host_file}")
    with open(host_file, 'w') as f:
        headings = """\\begin{longtable}{ll}
    \\toprule
    \\textbf{Host} & \textbf{\# extensions} \\\\ \midrule"""
        f.write(headings)
        for key in df.keys():
            #Adds host to output file
            key_value = key.replace('_','\\_')
            row = f"""
        {key_value} & {df[key].values[0]} \\\\"""
            f.write(row)

            #Adds host to dictionary 
            if key in count_hosts.keys():
                count_hosts[key] += df[key].values[0]
            else:
                count_hosts[key] = df[key].values[0]

            hosts[key] = df[key].values[0]

            #TODO Need to add table name
        footer = """\\bottomrule
\end{longtable}"""
        f.write(footer)
    
    individual_hosts.append(hosts)

count_hosts = dict(sorted(count_hosts.items(), key=lambda item: item[1], reverse=True))

#Generates a combined host file for all categories
#TODO Remove error
host_summary = os.path.join(output_dir, "host_summary.tex")
with open(host_summary, "w") as f:
    f.write("""\\begin{table}[h]
    \centering
    \\begin{tabular}{""")
    f.write(f"l{'c'*(len(names)+1)}")
    f.write("""} \\toprule""") 
    f.write("""
        Host & """)
    for name in names:
        f.write(name +" & ")

    f.write("Total \\\\ \midrule")
    for key in count_hosts:
        if count_hosts[key] <= 2:
            break

        line = """
        """+key.replace('_','\\_')
        
        for i in individual_hosts:
            if (key in i):
                line += " & " + str(i[key])
            else:
                line += " & 0"
                
        
        line += " & " + str(count_hosts[key]) + "\\\\"
        f.write(line)
    
    f.write("""
    \\bottomrule
    \end{tabular}
    \caption{Summary of host files}
    \label{tab:host_summary}
\end{table}
""")

#Count values in file
permissions_counts = pd.DataFrame()
ext_permissions = pd.DataFrame()
for file in csv_folders:
    file_name = file.split('/')[-1].replace("_", " ").capitalize()
    file = os.path.join(file,"permissions_and_info.csv")
    csv_filepath = os.path.join(cwd, file)
    df = pd.read_csv(csv_filepath)
    df.drop(columns=['None'], inplace=True)
    names= df.iloc[:, 9:].keys()
    total = df[names].sum()
    permissions_counts[file_name] = total

    #Work out the number of permissions requested per extension
    permissions_ext = df.iloc[:, 9:]
    permissions_ext['total'] = permissions_ext.sum(axis=1)
    new_df = pd.DataFrame()
    new_df['Extension'] = df['Name']
    new_df['Number of Permissions'] = permissions_ext['total']
    new_df['Category'] = file_name
    new_df = new_df.sort_values(by='Number of Permissions',ascending=False)
    ext_permissions = pd.concat([ext_permissions, new_df])
    print(ext_permissions)
    
sns.set_style('whitegrid')
sns.set_palette('colorblind')
ax = sns.countplot(data=ext_permissions, x='Number of Permissions',palette='colorblind', hue='Category')
#ax.set_title(title)
plt.xlabel('Number of permissions')
plt.ylabel("Number of extensions")
plt.savefig(os.path.join(output_dir, 'no_permissions.pgf'), bbox_inches='tight')
#plt.show()
matplotlib.pyplot.close()

print(f"Creating permission per app table at {os.path.join(output_dir, file_name +'_no_permissions.pgf')}")
"""
quit()
permissions = pd.DataFrame()
sns.set_style('whitegrid')
fig, ax = plt.subplots()

# Define a color palette for each file
color_palette = sns.color_palette('colorblind', n_colors=len(csv_folders))
legend_elements = [] 

for i, (file, color) in enumerate(zip(csv_folders, color_palette)):
    file_name = file.split('/')[-1]
    file = os.path.join(file, "permissions_and_info.csv")
    csv_filepath = os.path.join(cwd, file)
    df = pd.read_csv(csv_filepath)
    df.drop(columns=['None'], inplace=True)
    names = df.iloc[:, 9:].keys()
    total = df[names].sum()
    permissions[file_name] = total

    # Work out the number of permissions requested per extension
    permissions_ext = df.iloc[:, 9:].select_dtypes(include='number')
    permissions_ext['total'] = permissions_ext.sum(axis=1)
    new_df = pd.DataFrame()
    new_df['Extension'] = df['Name']
    new_df['Number of Permissions'] = permissions_ext['total']
    new_df = new_df.sort_values(by='Number of Permissions', ascending=True)

    print(new_df)

    # Use color parameter to set different colors for bars
    countplot = sns.countplot(data=new_df, x='Number of Permissions', palette=[color], ax=ax, alpha=0.7)

    # Create a custom legend element for each file
    legend_elements.append(Line2D([0], [0], color=color, label=file_name))

# Set x-axis labels and legend after the loop
ax.set_xticks(range(len(new_df['Number of Permissions'].unique())))
ax.set_xticklabels(new_df['Number of Permissions'].unique())
ax.legend(handles=legend_elements, title='Category', loc='upper right')

plt.xlabel('Number of permissions')
plt.ylabel("Number of extensions")


# Save the final combined plot
plt.savefig(os.path.join(output_dir, 'combined_plot_different_colors.pgf'), bbox_inches='tight')
plt.show()"""

#Only select numbers
numeric_cols = permissions_counts.select_dtypes(include='number')
#Get column totals
total_col = numeric_cols.sum()
#Get row totals
permissions_counts['Total'] = numeric_cols.sum(axis=1)
#Sort
permissions_counts = permissions_counts.sort_values(by='Total',ascending=False)
#Remove unnamed
permissions_counts.drop('Unnamed: 67')
#Add total row 
permissions_counts.loc['Total'] = total_col
#Make latex code
permissions_counts = permissions_counts.round(0)
latex_code = permissions_counts.to_latex(index=True, header=list(permissions_counts.columns),float_format='%.0f')

perm_file = os.path.join(output_dir, 'permissions.tex')
with open(perm_file, 'w') as f:
    f.write(latex_code)

print(f"Creating permission requested table at {perm_file}")
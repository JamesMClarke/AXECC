import common, argparse, os, sys, operator
import pandas as pd


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
        Search term & \# Extensions & Total users & Avg. \# users & Avg. rating & Avg. \# Permissions & Manifest V2 & Manifest V3\\\\ \midrule"""

#Create summary of permissions and info
with open(summary_file, 'w') as f:
    f.write(headings)

    for file in csv_folders:
        file = os.path.join(file,"permissions_and_info.csv")
        csv_filepath = os.path.join(cwd, file)
        df = pd.read_csv(csv_filepath)
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
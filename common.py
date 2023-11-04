from pathlib import Path

#Function to try create dir if it doesn't exist
def create_directory(directory_path):
    Path(directory_path).mkdir(parents=True, exist_ok=True)

#Function to sort a dictionary
def sort_dic(dic):
    return dict(sorted(dic.items(), key=lambda item: item[1], reverse=True))
from os import rename
from os.path import exists, join
from shutil import move
import json
import logging
import os
"""
FILE CLEANER SCRIPT - Will Run Twice a Day on my Mac to clean up any files that I may leave on my desktop 
the objective is to take files from my classes that I may have created or that I downloaded and go and automatically clean them up 

the program will determine where each of these files will be sent through the use of a special json file that keeps track of the special headers 
for example CS_448_Lecture_1.pt will have the header CS_448 once the file is read the header is removed and the only "lecture_1.pt" will be moved to 
a folder with the name CS_448 

"""
# Desktop path
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
headers_path = os.path.join(os.path.expanduser("~"), "Desktop", "headers.json")
logging.basicConfig(
    filename=f'{desktop_path}/cleaner_logfile.log',  # Specify the log file path
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_headers():
    if os.path.exists(headers_path):
        with open(headers_path, 'r') as file:
            return json.load(file)
    return []
def save_headers(names):
    with open(headers_path, 'w') as file:
        json.dump(names, file, indent=4)


def make_unique(dest, name):
    filename, extension = os.path.splitext(name)
    counter = 1

    # Construct the full path using os.path.join to ensure OS-agnostic behavior
    while os.path.exists(os.path.join(dest, name)):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name
def move_file(dest, entry):
    if exists(f"{dest}/{entry}"):
        unique_name = make_unique(dest, entry)
        oldName = join(dest, entry)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)


def remove_header(file_name):
    parts = file_name.split('_')
    if len(parts) > 1:
        new_filename = '_'.join(parts[2:])
    else:
        new_filename = file_name
    return new_filename

def check_unique(directory_path, base_name):
    with os.scandir(directory_path) as entries:
        for entry in entries:
            if base_name == entry.name:
                return False
    return True



def on_cleaner():
    headers = load_headers()
    lowercase_headers = tuple(header.lower() for header in headers)
    moved = False


    with os.scandir(desktop_path) as entries:
        for entry in entries:
            if entry.is_file():
                name = entry.name
                start = name.split("_")

                lowercase_name = name.lower()


                # Checks if the name of the file starts with one of the headers
                # checks if directory for this header exist if it does
                # not it needs to be created

                if lowercase_name.startswith(tuple(lowercase_headers)):
                    moved = True
                    # creates a directory path with this header
                    directory_path = os.path.join(desktop_path,f"{start[0]}_{start[1]}")

                    if not os.path.exists(directory_path):
                        # If it doesn't exist, create it
                        os.makedirs(directory_path)


                    # Before file is moved over the header needs to be removed
                    # this needs to be done before it is moved in order to
                    # more efficiently make the unique name
                    # would need to loop through all of the files in the directory to
                    # see which ones may contain this name

                    base_name = remove_header(name)

                    # checks if name is unqiue within the directory
                    # if not unique name needs to be made unique

                    if not check_unique(directory_path,base_name):
                        unique_name = make_unique(directory_path, base_name)
                        desintation_path = os.path.join(directory_path, unique_name)
                    else:
                        desintation_path = os.path.join(directory_path, base_name)

                    desktop_loc = os.path.join(desktop_path,name)

                    os.rename(desktop_loc,desintation_path)
                    report = f"Moved {desktop_loc} to {desintation_path}"
                    logging.info(report)

    if not moved:
        report = f"No Files moved"
        logging.info(report)



on_cleaner()

import sys
import os
from office365.sharepoint.webs.web import File
from Office365_api import SharePoint
import re
from pathlib import PurePath

# Root Directory path os files to upload
ROOT_DIR = sys.argv[1]
# Sharepoint folder name. May include subfolders to upload to
SHAREPOINT_FOLDER_NAME = sys.argv[2]
# File name pattern. Only upload files with this pattern
FILE_NAME_PATTERN = sys.argv[3]

def upload_files(folder, keyword=None):
    file_list = get_list_of_files(folder)
    for file in file_list:
        if keyword is None or keyword == 'None' or re.search(keyword, file[0]):
            file_content = get_file_content(file[1])
            SharePoint().upload_file(file[0], SHAREPOINT_FOLDER_NAME, file_content)

# get list of files in folder
def get_list_of_files(folder):
    file_list = []
    folder_item_list = os.listdir(folder)
    for item in folder_item_list:
        item_full_path = PurePath(folder, item)
        if os.path.isfile(item_full_path):
            file_list.append([item, item_full_path])
    return file_list

# read files and return the content of files
def get_file_content(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

if __name__ == '__main__':
    upload_files(ROOT_DIR, FILE_NAME_PATTERN)
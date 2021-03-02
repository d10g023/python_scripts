import json
import os
import datetime
import time
import shutil

# directory where script search from files
directory = "/path/to/dir"

# list of json files on path directory
listOfFiles = list()
for (dirpath, dirnames, filenames) in os.walk(directory):
    listOfFiles += [os.path.join(dirpath, file) for file in filenames if file[-5:] == ".json" ]

for line in listOfFiles:
    with open(line) as json_file:
        
        #load json file 
        data = json.load(json_file)
        
        try:
            if line[:-5].split("/")[-1] == data['title']:
                
                # get the creation time of file 
                date_json = data['photoTakenTime']['formatted'].split(",")
                date_json = date_json[0].split("/")

                source = str(line[:-5])
                target = str(directory[:-1])+"/order_fies/"+str(date_json[2])+"/"+str(date_json[1])
                
                # create dirs based on year and month 
                try:
                    os.makedirs(target)
                except OSError:
                    # if the dir exists, the makedirs will return an error. this except will keep the script running
                    pass

                # copy files from source to target order by year and month 
                try:
                    print("Copy file " + source)
                    shutil.copy2(source,target)
                except FileNotFoundError:
                    # in case of json file exist but the file in field title not, this except return this warning 
                    print("File " + data['title'] + " not found but the json file exist")

        except KeyError:
            # this execpt prevent the script exit if having json file without field name invalid  
            pass

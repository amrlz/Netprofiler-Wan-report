#!/usr/bin/python3
import requests
import urllib3
import json
import csv
import time
import os
from requests.auth import HTTPBasicAuth
from datetime import date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable ssl warning

data = []

with open('columnC.txt', 'r')as file1, open('columnD.txt', 'r', encoding='utf16')as file2:
    file1 = csv.reader(file1)
    file2 = csv.reader(file2)
    for i in file1:
        data.append(i[0])
    for i in file2:
        data.append(i[0])
        #print(i)

data = set(data) # Create a set with unique IP's

start = (int(time.time() // 86400)) * 86400 - 86400 # timestamp midnight yesterday 00:00

end = (int(time.time() // 86400)) * 86400  # timestamp for midnight today 00:00(will create a 24 hour report)

today = str(date.today()) # gives date as 2020-**-** -- using this to name the folder

path = "HostPair/" + today # path to create the folder which we use to save reports

os.mkdir(path) # linux command to will create the folder

for i in data:# looping line by line - i will be the IP
    i = i.replace('ï»¿','').replace('\ufeff','').split()
    i = ' '.join(i)
    csv_file = open(path + "/" + i+'.csv', 'w')# create a new file with the name of the interface
    csv_file.write("Server IP, Client IP, Total Bytes, Total Packets")
    csv_file.write(today)
    csv_file.write("\n")
    payload = {"criteria":{"time_frame":{"start":start,"end": end,"resolution":"hour"},"query":{"realm":"traffic_summary","host_group_type": "ByLocation","group_by":"hop","group_dev_iface": i, "limit":999999, "sort_column":30,"columns":[9,13,30,31,25,27]}},"template_id":184} # the actual template we use to post
    url = requests.post('https://localhost/api/profiler/1.11/reporting/reports.json',verify=False, auth=HTTPBasicAuth("admin", "admin"), json=payload) # initial API to post the report
    data = url.json()
    for k,v in data.items(): #loop trough reponse
        if k =='id': # retrieve id of the report
            url = requests.get('https://localhost/api/profiler/1.11/reporting/reports/'+ str(v) + '.json',verify=False, auth=HTTPBasicAuth("admin", "admin")) # API to check status of the report
            data = url.json()
            for a,b in data.items():#loop trough reponse
                if a == 'percent': 
                    while b < 100:# check percentage of the report -- if not 100% then  loop trough the API until b is equal to 100
                        url = requests.get('https://localhost/api/profiler/1.11/reporting/reports/'+ str(v) + '.json',verify=False, auth=HTTPBasicAuth("admin", "admin"))
                        data = url.json()
                        #print(data)
                        for c,d in data.items():
                            if c == 'percent':
                                b = d # update variable b which will be the percentage of the report. and repeat the process until b is equal 100
                                #print('fetching report for',i,b)
                    url = requests.get('https://localhost/api/profiler/1.11/reporting/reports/'+ str(v) + '/queries.json',verify=False, auth=HTTPBasicAuth("admin", "admin")) # API to check status of the report
                    data = url.json()
                    for a in data:#loop trough reponse
                        a = a['id']
                        url = requests.get('https://localhost/api/profiler/1.11/reporting/reports/'+ str(v) +'/queries/' + a + '.json?limit=999999&columns=9,13,30,31,25,27', verify=False, auth=HTTPBasicAuth("admin", "admin"))
                        data = url.json()
                        for k in data['data']:
                            k = ','.join(k)
                            k = k.replace('|',',')
                            #print(k)
                            csv_file.write(k)
                            csv_file.write("\n")
                            #print(data)
    print('Report for interface', i, 'complete') # print status.

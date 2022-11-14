# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:49:48 2022

@author: tomas.lenzi
"""

import hubspot
from hubspot.crm.owners import ApiException
import csv

client = hubspot.Client.create(access_token="YOUR ACCESS TOKEN")
headers = ['id','email','first_name','last_name'] # Example of properties you might want stored in the csv file
results_list = []
filepath = 'Filepath where you want to store your data'

# Loop to retrieve all the owners in your Hubspot account
try:
    api_response = client.crm.owners.owners_api.get_page(limit=100, archived=False)
    while True:
        for i in api_response._results:
            results_list.append(i)
        if api_response._paging != None:
            after = api_response._paging._next._after
            api_response = client.crm.owners.owners_api.get_page(limit=100, archived=False, after=after)
        else:
            break
except ApiException as e:
    print("Exception when calling owners_api->get_page: %s\n" % e)

print('%d owners added to the csv file' % len(results_list))

# Appending the new data to the csv
with open(filepath,'w',newline='\n') as csvfile:
    arquivo_csv = csv.writer(csvfile,delimiter=';',quotechar='|',quoting=csv.QUOTE_MINIMAL)
    arquivo_csv.writerow(headers)
    for owner in results_list:
        arquivo_csv.writerow([owner._id,owner._email,owner._first_name,owner.last_name])


    
    
    

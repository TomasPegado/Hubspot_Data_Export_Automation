# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 20:42:20 2022

@author: tomas.lenzi
"""

import hubspot
from hubspot.crm.objects.meetings import ApiException
import csv

def search(list_filter, subject):
    # Check if the meeting title are in the list of filters
    if subject == None:
        return True
    for filter in list_filter:
        if filter in subject:
            return True
        
def insert_data(results_list, api_response,list_filter, count):
    """
    Function that validates if the meeting match with all the filters,
    before  inserting in the results_list
    """
    for info in api_response._results:
        if search(list_filter, info._properties['hs_meeting_title']) != True:   
            results_list.append(info)
            count += 1
            print(info._created_at, count)
    return results_list, count

client = hubspot.Client.create(access_token="YOUR ACCESS TOKEN")
properties = ['hubspot_owner_id','hs_meeting_title','hs_meeting_end_time'] # Meetings´s properties you want in the api response
headers = ['hs_object_id','hubspot_owner_id','hs_meeting_end_time'] # The properties you want stored in the csv file
list_filters = [] # List of Meetings Titles you don´t want to extract
filepath = 'Filepath where you want to store the data'
results_list = []
count = 0

# Checking the last meeting id registered in the csv
with open(filepath, 'r') as csvfile:
    arquivo_csv = csv.reader(csvfile, delimiter=";")
    for linha in arquivo_csv:
        pass
    after = int(linha[0])+1 # we pass this variable as the after parameter in the API resquest,
                            # so we only look for contacts still not registered in the csv.

# Loop to retrieve all the meetings still not registered in your database
try:
    api_response = client.crm.objects.meetings.basic_api.get_page(limit=100, archived=False,properties=properties, after=after)
    while True:
        results_list, count = insert_data(results_list,api_response,list_filters, count)
        if api_response._paging != None:
            after = api_response._paging._next._after
            api_response = client.crm.objects.meetings.basic_api.get_page(limit=100, archived=False,properties=properties,after=after)
        else:
            break
except ApiException as e:
    print("Exception when calling basic_api->get_page: %s\n" % e)

print('%d meetings added to the list' % len(results_list))

# Appending the new data to the csv
if len(results_list) > 0:    
    with open(filepath,'a',newline='\n') as csvfile:
        arquivo_csv = csv.writer(csvfile,delimiter=';',quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for data in results_list:
            lista = []
            for inf in headers:
                lista.append(data._properties[inf])
            arquivo_csv.writerow(lista)

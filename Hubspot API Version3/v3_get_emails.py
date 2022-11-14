# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 19:37:54 2022

@author: tomas.lenzi
"""

import hubspot
from hubspot.crm.objects.emails import ApiException
import datetime
from dateutil.tz import tzutc
import csv

def search(list_filter, subject):
    # Check if the emails subject are in the list of filters
    if subject == None:
        return True
    for filter in list_filter:
        if filter in subject:
            return True
        
def insert_data(results_list, api_response,subjects_filter,count):
    """
    Function that validates if the email match with all the filters,
    before  inserting in the results_list
    """
    tamanho = len(api_response._results)
    lengh = len(results_list)
    for i in range(1,tamanho+1):
        if api_response._results[-i]._created_at > start_date:
            if search(subjects_filter, api_response._results[-i]._properties['hs_email_subject']) != True:   
                results_list.insert(lengh,api_response._results[-i])
                count += 1
                print(api_response._results[-i]._created_at,count)
        else:
            break
    return results_list , count

filepath = 'Filepath where you will store the data'
client = hubspot.Client.create(access_token="YOUR ACCESS TOKEN")
properties = ['hubspot_owner_id','hs_email_direction','hs_email_status','hs_email_subject'] # Emails´s properties you want in the api response
headers = ['hs_object_id','hubspot_owner_id','hs_email_status','hs_email_direction','hs_createdate']# The properties you want stored in the csv file
start_date = datetime.datetime(year=2021,day=1,month=1, tzinfo=tzutc()) # start date for the emails
subjects_filter = [] # List of Emails Subjects you don´t want to extract
results_list = []
count = 0

# Checking the last email id registered in the csv
with open(filepath, 'r') as csvfile:
    arquivo_csv = csv.reader(csvfile, delimiter=";")
    for linha in arquivo_csv:
        pass
    after= int(linha[0])+1 # we pass this variable as the after parameter in the API resquest,
                            # so we only look for contacts still not registered in the csv.

# Loop to retrieve all the emails still not registered in your database
try:
    api_response = client.crm.objects.emails.basic_api.get_page(limit=100, archived=False, properties=properties,after=after)
    while True:
        results_list, count = insert_data(results_list,api_response,subjects_filter,count)
        if api_response._paging != None:
            after = api_response._paging._next._after
            api_response = client.crm.objects.emails.basic_api.get_page(limit=100, archived=False, properties=properties, after=after)
        else:
            break
except ApiException as e:
    print("Exception when calling basic_api->get_page: %s\n" % e)
    
print('%d emails retrieved' % len(results_list))    

# Appending the new data to the csv
if results_list > 0:
    with open(filepath,'a',newline='\n') as csvfile:
        arquivo_csv = csv.writer(csvfile,delimiter=';',quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for data in results_list:
            lista = []
            for inf in headers:
                lista.append(data._properties[inf])
            arquivo_csv.writerow(lista)
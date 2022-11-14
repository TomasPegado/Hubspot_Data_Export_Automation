# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 20:07:22 2022

@author: tomas.lenzi
"""
import hubspot
from hubspot.crm.contacts import ApiException
import csv

def insert_data(results_list,api_response,count):
    """
    Function that validates if the contact has an email registered,
    before  inserting in the results_list
    """
    for info in api_response._results:
        if info._properties['email'] != None:
            results_list.append(info)
            count += 1
            print(results_list[-1]._properties['createdate'], count)
    return results_list , count

filepath = 'filepath where you will store the data'
client = hubspot.Client.create(access_token="YOUR ACCESS TOKEN")
properties = ['firstname','lastname','createdate','email','hubspot_owner_id'] # Contact´s properties you want in the api response
headers = ['hs_object_id','hubspot_owner_id','firstname','lastname','email','createdate'] # Example of properties you might want stored in the csv file
results_list = []
unicode_error_list = []
count = 0

# Checking the last contact id registered in the csv
with open(filepath, 'r') as csvfile: 
    arquivo_csv = csv.reader(csvfile, delimiter=";")
    for linha in arquivo_csv:
        pass
    after= int(linha[0])+1 # we pass this variable as the after parameter in the API resquest,
                            # so we only look for contacts still not registered in the csv.

# Loop to retrieve all the contacts still not registered in your database
try:
    api_response = client.crm.contacts.basic_api.get_page(limit=100, archived=False, properties=properties, after=after)
    while True:
        results_list , count = insert_data(results_list, api_response,count)
        if api_response._paging != None:
            after = api_response._paging._next._after
            api_response = client.crm.contacts.basic_api.get_page(limit=100, archived=False, properties=properties, after=after)
        else:
            break
except ApiException as e:
    print("Exception when calling basic_api->get_page: %s\n" % e)
    
print('%d contacts added to the list' % len(results_list))

# Appending the new data to the csv
if len(results_list) > 0:
    with open(filepath,'a',newline='\n') as csvfile:
        arquivo_csv = csv.writer(csvfile,delimiter=';',quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for data in results_list:
            try:
                lista = []
                for inf in headers:
                    lista.append(data._properties[inf])
                arquivo_csv.writerow(lista)  
            except UnicodeEncodeError:
                unicode_error_list.append(data)

    inserted = len(results_list) - len(unicode_error_list)
    errors = len(unicode_error_list)
    print("%d dados adicionados ao csv \n %d contacts were unable to be added to the csv" % (inserted, errors))



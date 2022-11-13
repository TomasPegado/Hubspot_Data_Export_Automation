# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 16:58:57 2022

@author: tomas.lenzi
"""

import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

#Getting all contatcs information
propriedades = 'firstname&property=lastname&property=createdate&property=email&property=hubspot_owner_id&property=contactowner' #example of how to construct the property parameter
max_results = 10000 #You can change this
access_token = 'YOUR ACESS TOKEN' 
count = 10
contact_list = []
parameters = f'count={count}&property={propriedades}'
lengh_parameters = len(parameters)
get_all_contacts_url = "https://api.hubapi.com/contacts/v1/lists/all/contacts/all?"
headers = {'Authorization': f'Bearer {access_token}'}

has_more = True
while has_more:
    get_url = get_all_contacts_url + parameters
    r = requests.get(url= get_url, headers = headers)
    response_dict = r.json()
    has_more = response_dict['has-more']
    contact_list.extend(response_dict['contacts'])
    parameters= parameters[:lengh_parameters]+f"&vidOffset={str(response_dict['vid-offset'])}"
    if len(contact_list) >= max_results:
        print('maximum number of results exceeded')
        break
            
print('loop finished')

list_length = len(contact_list) 

print("You've succesfully parsed through {} contact records and added them to a list".format(list_length))

contatos = pd.DataFrame()
for i in range(len(contact_list)): #Criar o DataFrame dos contatos
    
    ctt = pd.DataFrame.from_dict(contact_list[i]['properties'])
    
    frames = [contatos, ctt]
    contatos = pd.concat(frames)

contatos.reset_index(drop=True,inplace=True)
contatos.rename(columns={'hubspot_owner_id': 'ownerId'}, inplace=True)

for i in range(len(contatos)): #Mudar o formato dos dados
    
    l = float(contatos['lastmodifieddate'][i])/1000
    c = float(contatos['createdate'][i])/1000
    
    last = datetime.fromtimestamp(l, tz = ZoneInfo("America/Sao_Paulo"))
    created = datetime.fromtimestamp(c, tz = ZoneInfo("America/Sao_Paulo"))
    
    contatos['lastmodifieddate'][i] = last.strftime("%d/%m/%Y")
    contatos['createdate'][i] = created.strftime("%d/%m/%Y")

    
#Owners information
url = "https://api.hubapi.com/owners/v2/owners"
r = requests.get(url= url, headers = headers)
req = r.json()
owners = pd.DataFrame.from_dict(req)
for i in range(len(owners)):    
    owners['ownerId'][i] = str(owners['ownerId'][i])


#Merge dos dataframes
hub_contacts_df = pd.merge(
    owners[['ownerId','firstName','lastName']],
    contatos,
    how='right',
    on='ownerId')

hub_contacts_df['Contact_Owner'] =''
for i in range(len(hub_contacts_df)):
    
    hub_contacts_df['firstName'][i] = str(hub_contacts_df['firstName'][i])
    hub_contacts_df['lastName'][i] = str(hub_contacts_df['lastName'][i])
    
    if hub_contacts_df['firstName'][i] != 'nan':
        
        hub_contacts_df['Contact_Owner'][i] = hub_contacts_df['firstName'][i]+' '+hub_contacts_df['lastName'][i]
    
hub_contacts_df.drop(columns = ['firstName','lastName'], inplace=True)


#Criando arquivo csv
filepath = Path('filepath')
hub_contacts_df.to_csv(filepath, index=False)



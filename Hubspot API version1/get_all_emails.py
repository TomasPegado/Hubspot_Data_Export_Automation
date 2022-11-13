# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 16:05:03 2022

@author: tomas.lenzi
"""

import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

url_eng = 'https://api.hubapi.com/engagements/v1/engagements/paged?'
max_results = 10000
access_token = 'YOUR ACCESS TOKEN' 
count = 250
email_list = []
headers = {'Authorization': f'Bearer {access_token}'}
parametros = f'count={count}'
lengh_parametro = len(parametros)

has_more = True
while has_more:
    get_url = url_eng + parametros
    r = requests.get(url= get_url, headers = headers)
    response_dict = r.json()
    has_more = response_dict['hasMore']
    lista = [i for i in response_dict['results'] if i['engagement']['type'] == 'EMAIL']
    email_list.extend(lista)
    parametros= parametros[:lengh_parametro]+f"&offset={str(response_dict['offset'])}"
    if len(email_list) >= max_results:
        print('maximum number of results exceeded')
        break
            
print('loop finished')

list_length = len(email_list) 

print("You've succesfully parsed through {} engagement records and added them to a list".format(list_length))


#Criando o Dataframe
emails = pd.DataFrame(columns=['Body','ownerId','Data','Status','PostSendStatus','subject','CompanyId','contactId'])
for i in email_list:
    owner = i['engagement']['ownerId']
    d = float(i['engagement']['timestamp'])/1000
    data = datetime.fromtimestamp(d, tz = ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")
    company = i['associations']['companyIds']
    contact = i['associations']['contactIds']
    
    if 'bodyPreview' in i['engagement'].keys():
        body = i['engagement']['bodyPreview']
    else:
        body = None
        
    if 'status' in i['metadata'].keys():
        status = i['metadata']['status']
    else:
        status = None
    
    if 'postSendStatus' in i['metadata'].keys():
        postatus = i['metadata']['postSendStatus']
    else:
        postatus = None
        
    if 'subject' in i['metadata'].keys():
        subject = i['metadata']['subject']
    else:
        subject = None
         
    df = pd.DataFrame([[body,owner,data,status,postatus,subject,company,contact]],columns=['Body','ownerId','Data','Status','PostSendStatus','subject','CompanyId','contactId'])
    frames = [emails,df]
    emails = pd.concat(frames)

#Trocando o Id pelo nome do Owner
url = "https://api.hubapi.com/owners/v2/owners"
r = requests.get(url= url, headers = headers)
req = r.json()
owners = pd.DataFrame.from_dict(req)
for i in range(len(owners)):
    owners['ownerId'][i] = int(owners['ownerId'][i])

#Merge dos dataframes
email_hub_df = pd.merge(
    owners[['ownerId','firstName','lastName']],
    emails,
    how='right',
    on='ownerId')

email_hub_df['Contact_Owner'] =''
for i in range(len(email_hub_df)):
    
    email_hub_df['firstName'][i] = str(email_hub_df['firstName'][i])
    email_hub_df['lastName'][i] = str(email_hub_df['lastName'][i])
    
    if email_hub_df['firstName'][i] != 'nan':
        
        email_hub_df['Contact_Owner'][i] = email_hub_df['firstName'][i]+' '+email_hub_df['lastName'][i]
    
email_hub_df.drop(columns = ['firstName','lastName'], inplace=True)

filepath = Path('filepath')
email_hub_df.to_json(filepath, orient="table")








    



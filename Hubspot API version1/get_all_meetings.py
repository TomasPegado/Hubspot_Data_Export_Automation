# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 17:51:01 2022

@author: tomas.lenzi
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

url_eng = 'https://api.hubapi.com/engagements/v1/engagements/paged?'
# max_results = 10000
access_token = 'YOUR ACCESS TOKEN' 
count = 250
meeting_list = []
headers = {'Authorization': f'Bearer {access_token}'}
parametros = f'count={count}'
lengh_parametro = len(parametros)


has_more = True
while has_more:
    get_url = url_eng + parametros
    r = requests.get(url= get_url, headers = headers)
    response_dict = r.json()
    has_more = response_dict['hasMore']
    lista = [i for i in response_dict['results'] if i['engagement']['type'] == 'MEETING' or i['engagement']['type'] == 'CALL']
    meeting_list.extend(lista)
    parametros= parametros[:lengh_parametro]+f"&offset={str(response_dict['offset'])}"
    # if len(meeting_list) >= max_results:
    #     print('maximum number of results exceeded')
    #     break
            
print('loop finished')

list_length = len(meeting_list) 

print("You've succesfully parsed through {} engagement records and added them to a list".format(list_length))

#Creating a Dataframe
meetings = pd.DataFrame(columns=['Body','OwnerId','StartTime','ContactId','CompanyId'])
for i in meeting_list:
    owner = i['engagement']['ownerId']
    contact = i['associations']['contactIds']
    company = i['associations']['companyIds']
    
    if i['engagement']['type'] != 'CALL':
        starttime = i['metadata']['startTime']
    else:
        starttime = i['engagement']['timestamp']
        
    if 'bodyPreview' in i['engagement'].keys():
        body = i['engagement']['bodyPreview']
    else:
        body = None
        
    df = pd.DataFrame([[body,owner,starttime,contact,company]],columns=['Body','ownerId','StartTime','ContactId','CompanyId'])
    frames = [meetings,df]
    meetings = pd.concat(frames)

#Change the Owner_ID for the Owner Name
url = "https://api.hubapi.com/owners/v2/owners"
r = requests.get(url= url, headers = headers)
req = r.json()
owners = pd.DataFrame.from_dict(req)
for i in range(len(owners)):
    owners['ownerId'][i] = str(owners['ownerId'][i])


##Merge of the dataframes
meetings_hub_df = pd.merge(
    owners[['ownerId','firstName','lastName']],
    meetings,
    how='right',
    on='ownerId')

meetings_hub_df['Contact_Owner'] =''
for i in range(len(meetings_hub_df)):
    
    meetings_hub_df['firstName'][i] = str(meetings_hub_df['firstName'][i])
    meetings_hub_df['lastName'][i] = str(meetings_hub_df['lastName'][i])
    
    if meetings_hub_df['firstName'][i] != 'nan':
        
        meetings_hub_df['Contact_Owner'][i] = meetings_hub_df['firstName'][i]+' '+meetings_hub_df['lastName'][i]
    
meetings_hub_df.drop(columns = ['firstName','lastName'], inplace=True)

for i in range(len(meetings_hub_df)): #Dealing with date values    
    s = float(meetings_hub_df['StartTime'][i])/1000
    created = datetime.fromtimestamp(s, tz = ZoneInfo("America/Sao_Paulo"))
    meetings_hub_df['StartTime'][i] = created.strftime("%d/%m/%Y")


#Converting to a csv
filepath = Path('filepath')
meetings_hub_df.to_csv(filepath, index=False)
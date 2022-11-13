# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 18:22:29 2022

@author: tomas.lenzi
"""
import requests
import pandas as pd
from pathlib import Path

access_token="YOUR ACCESS TOKEN"
headers = {'Authorization': f'Bearer {access_token}'}
url = "https://api.hubapi.com/owners/v2/owners"

r = requests.get(url= url, headers = headers)

req = r.json()

owners = pd.DataFrame.from_dict(req)

for i in range(len(owners)):
    owners['ownerId'][i] = str(owners['ownerId'][i])
    
#Creating the Dataframe
filepath = Path('filepath')
owners.to_csv(filepath, index=False)

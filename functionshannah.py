import pandas as pd
from datetime import datetime
import math

# Function to clean up current file
def og_cleanup(x):
    x.rename(columns={'Contract ID': 'Contract_ID', 'Current Rate': 'Current_Rate', 'Start date': 'Start_Date'}, inplace = True)
    x['Current_Rate']=pd.to_numeric(x['Current_Rate'], errors='coerce').fillna(0)
    x['Start_Date'] = x['Start_Date'].dt.month

# Function to clean up Steven's File
def sw_cleanup(x):
    x.rename(columns={'Contract ID': 'Contract_ID', 'Current Rate': 'Current_Rate', 'New or Renewal': 'New_or_Renewal'}, inplace = True)
    x['Current_Rate'] = pd.to_numeric(x['Current_Rate'], errors='coerce').fillna(0)


#Checking for Exceptions
def smart_check(row):
    currentM = datetime.now().month
    if row['Agent_x'] != row['Agent_y']:
        if row['Renewal/New'] == 'Renewal':
            return "Agent Missmatch due to New or Renewal"
        elif row['Renewal/New'] == 'New':
            return "Agent Missmatch due to New or Renewal"
        else:
            return "Agent Missmatch"

    if row['Current_Rate_x'] != row['Current_Rate_y']:
        if int(row['Current_Rate_x']) == row['Current_Rate_y'] - 5 and currentM == row['Start_Date']:
            return "Rate Mismatch Contract entered new year cycle"
        else:
            return "Rate Mismatch"
    else:
        return ''

# Merging Fucntion
def merger(x,y):
    y = pd.merge(x, y, how='outer', on='Contract_ID')
    x["Exceptions"] = y.apply(lambda row: smart_check(row), axis=1)

#%%
import pandas as pd
import numpy as np

df = pd.read_csv('DAILY DATA/FA_Q_FULL.csv')

df['YEAR'] = df['DATE'].str.split('Q').str[0]
df['YEAR'] = df['YEAR'].astype(int)

# Filter by dates
df = df[(df['YEAR'] >= 2016)]

IS = ['Net_Revenue','Gross_Profit', 'EBIT', 'EBITDA',  'NPATMI']
MARGIN = ['Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin','NPAT_Margin']
BS = ['Total_Asset', 'Cash', 'Cash_Equivalent', 'Inventory', 'Account_Receivable','Tangible_Fixed_Asset', 
      'Total_Liabilities', 'ST_Debt', 'LT_Debt',
      'TOTAL_Equity','Invested_Capital']
CF = ['Operating_CF', 'Dep_Expense', 'Inv_CF', 'Capex', 'Fin_CF', 'FCF']

# Filter by core key codes
df = df[df['KEYCODE'].isin(IS + BS + CF + MARGIN)]
df = df.sort_values(by=['TICKER', 'KEYCODE', 'DATE'])

# Calculate YoY for IS item
df['YoY'] = df.groupby(['TICKER','KEYCODE'])['VALUE'].pct_change(periods = 4,fill_method=None)

#%%
df.to_csv('FA_processed.csv', index=False)
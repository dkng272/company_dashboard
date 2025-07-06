#%% Load dependencies
import pandas as pd
import numpy as np

#%% Load financial data
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

df.to_csv('Company Dashboard Project/FA_processed.csv', index=False)

#%% Load and clean valuation data
def load_valuation_data():
    # Load and prepare valuation metrics
    df = pd.read_csv('/Users/duynguyen/Library/CloudStorage/GoogleDrive-nkduy96@gmail.com/My Drive/Python/DAILY DATA/VALUATION.csv')
    df['TICKER'] = df['PRIMARYSECID'].str[:3]
    df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'])
    df = df.drop(columns=['PRIMARYSECID']).sort_values(by=['TICKER', 'TRADE_DATE']).reset_index(drop=True)

    # Rename valuation columns for easier access
    df.rename(columns={
        'PE_RATIO': 'P/E',
        'PX_TO_BOOK_RATIO': 'P/B',
        'PX_TO_SALES_RATIO': 'P/S'
    }, inplace=True)

    # Load and merge EV/EBITDA data
    ebitda = pd.read_csv('/Users/duynguyen/Library/CloudStorage/GoogleDrive-nkduy96@gmail.com/My Drive/Python/DAILY DATA/EVEBITDA.csv')
    ebitda.rename(columns={'DATE': 'TRADE_DATE', 'VALUE': 'EV/EBITDA'}, inplace=True)
    ebitda['TRADE_DATE'] = pd.to_datetime(ebitda['TRADE_DATE'])

    # Drop irrelevant columns before merge
    ebitda = ebitda.drop(columns=['KEYCODE', 'KEYCODENAME', 'ORGANCODE'])

    # Merge EV/EBITDA into main DataFrame
    df = pd.merge(df, ebitda, on=['TICKER', 'TRADE_DATE'], how='left')

    # Reorder columns for readability
    df = df[['TICKER', 'TRADE_DATE', 'P/E', 'P/B', 'P/S', 'EV/EBITDA']]

    return df

df = load_valuation_data()
df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'])
max_date = df['TRADE_DATE'].max()
five_years_ago = pd.to_datetime(max_date) - pd.DateOffset(years=5)
df = df[df.TRADE_DATE >= five_years_ago]

df.to_csv('/Users/duynguyen/Library/CloudStorage/GoogleDrive-nkduy96@gmail.com/My Drive/Python/Company Dashboard Project/Val_processed.csv', index=False)

#%% Get market cap data
def load_market_cap():
    mcap = pd.read_csv('G:\My Drive\Python\DAILY DATA\MARKET_CAP.csv')
    mcap['TRADE_DATE'] = pd.to_datetime(mcap['TRADE_DATE'])
    latest = mcap['TRADE_DATE'].max()
    mcap_today = mcap[mcap['TRADE_DATE'] == latest].copy()
    mcap_today['TICKER'] = mcap_today['PRIMARYSECID'].str[:3]
    mcap_today['CUR_MKT_CAP'] = mcap_today['CUR_MKT_CAP'] / 10**3
    # Remove the 'PRIMARYSECID' column as it is not needed for further analysis
    mcap_today.drop(columns='PRIMARYSECID', inplace=True)
    # Reordering the columns
    mcap_today = mcap_today[['TICKER', 'CUR_MKT_CAP', 'TRADE_DATE']]
    return mcap_today

df = load_market_cap()

df.to_csv('G:\My Drive\Python\Company Dashboard Project\MktCap_processed.csv', index=False)

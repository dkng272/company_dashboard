#%%
import streamlit as st
import pandas as pd
from typing import Literal
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#%% Data preparation
df = pd.read_csv('G:\My Drive\Python\Company Dashboard Project\FA_processed.csv')

IS = ['Net_Revenue','Gross_Profit', 'EBIT', 'EBITDA',  'NPATMI']
MARGIN = ['Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin','NPAT_Margin']
BS = ['Total_Asset', 'Cash', 'Cash_Equivalent', 'Inventory', 'Account_Receivable','Tangible_Fixed_Asset', 
      'Total_Liabilities', 'ST_Debt', 'LT_Debt',
      'TOTAL_Equity','Invested_Capital']
CF = ['Operating_CF', 'Dep_Expense', 'Inv_CF', 'Capex', 'Fin_CF', 'FCF']

#%% Financial data table
def create_fs_table(df, ticker: str) -> pd.DataFrame:
    global IS, BS, CF
    
    df_temp = df.copy()
    
    df_ticker = df_temp[df_temp['TICKER'] == ticker]  # Filter by ticker
    # df_ticker = df_temp[df_temp['TICKER'] == 'MWG']  # For debugging
    
    def process_section(section: list, section_name: str) -> pd.DataFrame: #function for displaying data
        df_section = df_ticker[df_ticker['KEYCODE'].isin(section)]
        section_table = df_section.pivot(index='KEYCODE', columns='DATE', values='VALUE')
        section_table = section_table.reindex(section)
        section_table = section_table.applymap(lambda x: f"{x/1e9:,.1f}") if section is not MARGIN else section_table
        section_table = section_table.applymap(lambda x: f"{x*100:.1f}%") if section is MARGIN else section_table
        # section_table = section_table.applymap(lambda x: f"{x:,.1f}")
        section_table.insert(0, 'SECTION', section_name)
        return section_table
    
    IS_growth = {i:f"{i}_Gr" for i in IS}

    def process_growth(section: list, section_name: str) -> pd.DataFrame: #function for displaying growth data
        df_growth = df_ticker[df_ticker['KEYCODE'].isin(section)]
        df_growth['YoY'] = df_growth.groupby(['TICKER','KEYCODE'])['VALUE'].pct_change(periods = 4)
        growth_table = df_growth.pivot(index = 'KEYCODE', columns = 'DATE', values = 'YoY')
        growth_table = growth_table.reindex(section)
        growth_table = growth_table.rename(index = IS_growth)
        growth_table = growth_table.applymap(lambda x: f"{x*100:.1f}%") #format to %
        growth_table.insert(0, 'SECTION', section_name)
        return growth_table

    IS_table = process_section(IS, 'IS')
    GR_table = process_growth(IS,'IS_GROWTH')
    MARGIN_table = process_section(MARGIN, 'MARGIN')
    BS_table = process_section(BS, 'BS')
    CF_table = process_section(CF, 'CF')
    
    fs_table = pd.concat([IS_table, GR_table, MARGIN_table, BS_table, CF_table])
    fs_table = fs_table.drop(columns = 'SECTION')
    return fs_table

#%% Plotting key FA data
def create_FA_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[(df_temp.TICKER == ticker) & (df_temp.KEYCODE.isin(IS))]
    df_ticker = df_ticker.pivot(index='DATE', columns='KEYCODE', values='VALUE')
    df_ticker = df_ticker / 1e9     #divide all values by 10^9

    # Calculate 4-period moving averages for each metric
    ma = df_ticker[['Net_Revenue', 'Gross_Profit', 'EBIT', 'NPATMI']].rolling(window=4, min_periods=1).mean()

    # Create subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Net Revenue', 'Gross Profit', 'EBIT', 'NPATMI')
    )

    # Add traces for each metric and its moving average
    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['Net_Revenue'], name='Revenue', marker_color='royalblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['Net_Revenue'], mode='lines', name='Revenue MA(4)', line=dict(color='red')),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['Gross_Profit'], name='Gross Profit', marker_color='darkorange'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['Gross_Profit'], mode='lines', name='Gross Profit MA(4)', line=dict(color='red')),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['EBIT'], name='EBIT', marker_color='green'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['EBIT'], mode='lines', name='EBIT MA(4)', line=dict(color='red')),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['NPATMI'], name='NPATMI', marker_color = 'gray'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['NPATMI'], mode='lines', name='NPATMI MA(4)', line=dict(color='red')),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        title_text="Income Statement Overview - " + ticker,
        showlegend=False,
        height=800,
        width=1000,
        template="simple_white"
    )

    # Update y-axes labels
    fig.update_yaxes(ticksuffix="bn")

    # Show the plot
    fig.show()

def create_gr_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[(df_temp.TICKER == ticker) & (df_temp.KEYCODE.isin(IS))]
    df_ticker = df_ticker.pivot(index='DATE', columns='KEYCODE', values='YoY')
    df_ticker = df_ticker * 100

    # Calculate 4-period moving averages for each metric
    ma = df_ticker[['Net_Revenue', 'Gross_Profit', 'EBIT', 'NPATMI']].rolling(window=4, min_periods=1).mean()

    # Create subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Net Revenue', 'Gross Profit', 'EBIT', 'NPATMI')
    )

    # Add traces for each metric and its moving average
    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['Net_Revenue'], name='Revenue Growth', marker_color='royalblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['Net_Revenue'], mode='lines', name='Net Revenue MA(4)', line=dict(color='red')),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['Gross_Profit'], name='Gross Profit Growth', marker_color='darkorange'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['Gross_Profit'], mode='lines', name='Gross Profit MA(4)', line=dict(color='red')),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['EBIT'], name='EBIT Growth', marker_color='green'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['EBIT'], mode='lines', name='EBIT MA(4)', line=dict(color='red')),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['NPATMI'], name='NPATMI Growth', marker_color = 'gray'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['NPATMI'], mode='lines', name='NPATMI MA(4)', line=dict(color='red')),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        title_text="Income Statement Overview - " + ticker,
        showlegend=False,
        height=800,
        width=1000,
        template="simple_white"
    )

    # Update y-axes labels
    fig.update_yaxes(ticksuffix="%")

    # Show the plot
    fig.show()

def create_margin_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[(df_temp.TICKER == ticker) & (df_temp.KEYCODE.isin(MARGIN))]

    # Adjust data usage depending on the needs
    df_ticker = df_ticker.pivot(index='DATE', columns='KEYCODE', values='VALUE')
    df_ticker = df_ticker * 100

    # Calculate 4-period moving averages for each metric
    ma = df_ticker[['Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin', 'NPAT_Margin']].rolling(window=4, min_periods=1).mean()

    # Create subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Gross Margin', 'EBIT Margin', 'EBITDA Margin', 'NPAT Margin')
    )

    # Add traces for each metric and its moving average
    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['Gross_Margin'], name='Gross Margin', marker_color='royalblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['Gross_Margin'], mode='lines', name='Gross Margin MA(4)', line=dict(color='red')),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['EBIT_Margin'], name='EBIT Margin', marker_color='darkorange'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['EBIT_Margin'], mode='lines', name='EBIT Margin MA(4)', line=dict(color='red')),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['EBITDA_Margin'], name='EBITDA Margin', marker_color='green'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['EBITDA_Margin'], mode='lines', name='EBITDA Margin MA(4)', line=dict(color='red')),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(x=df_ticker.index, y=df_ticker['NPAT_Margin'], name='NPAT Margin', marker_color='gray'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=df_ticker.index, y=ma['NPAT_Margin'], mode='lines', name='NPAT Margin MA(4)', line=dict(color='red')),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        title_text="Margins Overview - " + ticker,
        showlegend=False,
        height=800,
        width=1000,
        template="simple_white"
    )

    # Update y-axes labels
    fig.update_yaxes(ticksuffix="%")

    # Show the plot
    fig.show()

#%%
table = create_fs_table(df, 'MWG')
fig1 = create_FA_plots(df, 'MWG')
fig2 = create_gr_plots(df, 'MWG')
fig3 = create_margin_plots(df, 'MWG')

#%%
def download_fs_table(ticker):
    fs_table = create_fs_table(df, ticker)
    return fs_table.to_excel(f"FS/{ticker}_FS.xlsx")

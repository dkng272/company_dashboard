#%%
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#%% Data preparation
df = pd.read_csv('FA_processed.csv')
val = pd.read_csv('Val_processed.csv')
mcap = pd.read_csv('MktCap_processed.csv')
bank = pd.read_csv('BankSupp_processed.csv')

# List creation
IS = ['Net_Revenue','Gross_Profit', 'EBIT', 'EBITDA',  'NPATMI']
MARGIN = ['Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin','NPAT_Margin']
BS = ['Total_Asset', 'Cash', 'Cash_Equivalent', 'Inventory', 'Account_Receivable','Tangible_Fixed_Asset', 
      'Total_Liabilities', 'ST_Debt', 'LT_Debt',
      'TOTAL_Equity','Invested_Capital']
CF = ['Operating_CF', 'Dep_Expense', 'Inv_CF', 'Capex', 'Fin_CF', 'FCF']

IS_ORDER = [
    "Net_Revenue",
    "Net_Revenue_Gr",
    "Gross_Profit",
    "Gross_Profit_Gr",
    "Gross_Margin",
    "EBIT",
    "EBIT_Gr",
    "EBIT_Margin",
    "EBITDA",
    "EBITDA_Gr",
    "EBITDA_Margin",
    "NPATMI",
    "NPATMI_Gr",
    "NPAT_Margin"
]


#%% Financial data table
def create_fs_table_main(df, ticker: str) -> pd.DataFrame:
    global IS, MARGIN
    df_temp = df.copy()
    df_ticker = df_temp[df_temp['TICKER'] == ticker]
    def process_section(section: list, section_name: str) -> pd.DataFrame:
        df_section = df_ticker[df_ticker['KEYCODE'].isin(section)]
        section_table = df_section.pivot(index='KEYCODE', columns='DATE', values='VALUE')
        section_table = section_table.reindex(section)
        section_table = section_table.map(lambda x: f"{x/1e9:,.1f}") if section is not MARGIN else section_table
        section_table = section_table.map(lambda x: f"{x*100:.1f}%") if section is MARGIN else section_table
        section_table.insert(0, 'SECTION', section_name)
        return section_table
    IS_growth = {i:f"{i}_Gr" for i in IS}
    def process_growth(section: list, section_name: str) -> pd.DataFrame:
        df_growth = df_ticker[df_ticker['KEYCODE'].isin(section)]
        # df_growth['YoY'] = df_growth.groupby(['TICKER','KEYCODE'])['VALUE'].pct_change(periods = 4)
        growth_table = df_growth.pivot(index = 'KEYCODE', columns = 'DATE', values = 'YoY')
        growth_table = growth_table.reindex(section)
        growth_table = growth_table.rename(index = IS_growth)
        growth_table = growth_table.map(lambda x: f"{x*100:.1f}%")
        growth_table.insert(0, 'SECTION', section_name)
        return growth_table
    IS_table = process_section(IS, 'IS')
    GR_table = process_growth(IS,'IS_GROWTH')
    MARGIN_table = process_section(MARGIN, 'MARGIN')
    fs_table = pd.concat([IS_table, GR_table, MARGIN_table])
    fs_table = fs_table.drop(columns = 'SECTION')
    fs_table = fs_table.reindex(index=IS_ORDER)  # Reorder columns based on IS_ORDER
    return fs_table

def create_fs_table(df, ticker: str) -> pd.DataFrame:
    global IS, BS, CF
    
    df_temp = df.copy()
    
    df_ticker = df_temp[df_temp['TICKER'] == ticker]  # Filter by ticker
    # df_ticker = df_temp[df_temp['TICKER'] == 'MWG']  # For debugging
    
    def process_section(section: list, section_name: str) -> pd.DataFrame: #function for displaying data
        df_section = df_ticker[df_ticker['KEYCODE'].isin(section)]
        section_table = df_section.pivot(index='KEYCODE', columns='DATE', values='VALUE')
        section_table = section_table.reindex(section)
        section_table = section_table.map(lambda x: f"{x/1e9:,.1f}") if section is not MARGIN else section_table
        section_table = section_table.map(lambda x: f"{x*100:.1f}%") if section is MARGIN else section_table
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
        growth_table = growth_table.map(lambda x: f"{x*100:.1f}%") #format to %
        growth_table.insert(0, 'SECTION', section_name)
        return growth_table

    IS_table = process_section(IS, 'IS')
    GR_table = process_growth(IS,'IS_GROWTH')
    MARGIN_table = process_section(MARGIN, 'MARGIN')
    fs_table = pd.concat([IS_table, GR_table, MARGIN_table])
    fs_table = fs_table.drop(columns = 'SECTION')
    return fs_table

def create_bs_table(df, ticker: str) -> pd.DataFrame:
    global BS
    df_temp = df.copy()
    df_ticker = df_temp[df_temp['TICKER'] == ticker]
    df_section = df_ticker[df_ticker['KEYCODE'].isin(BS)]
    section_table = df_section.pivot(index='KEYCODE', columns='DATE', values='VALUE')
    section_table = section_table.reindex(BS)
    section_table = section_table.map(lambda x: f"{x/1e9:,.1f}")
    return section_table

def create_cf_table(df, ticker: str) -> pd.DataFrame:
    global CF
    df_temp = df.copy()
    df_ticker = df_temp[df_temp['TICKER'] == ticker]
    df_section = df_ticker[df_ticker['KEYCODE'].isin(CF)]
    section_table = df_section.pivot(index='KEYCODE', columns='DATE', values='VALUE')
    section_table = section_table.reindex(CF)
    section_table = section_table.map(lambda x: f"{x/1e9:,.1f}")
    return section_table

#%% Plotting key FA data
def create_FA_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[(df_temp.TICKER == ticker) & (df_temp.KEYCODE.isin(IS))]
    df_ticker = df_ticker.pivot(index='DATE', columns='KEYCODE', values='VALUE')
    df_ticker = df_ticker / 1e9

    plot_cols = [col for col in ['Net_Revenue', 'Gross_Profit', 'EBIT', 'NPATMI'] if col in df_ticker.columns]
    if not plot_cols:
        return go.Figure()
    ma = df_ticker[plot_cols].rolling(window=4, min_periods=1).mean()
    subplot_titles = [col.replace('_', ' ') for col in plot_cols]
    n = len(plot_cols)
    rows = (n + 1) // 2
    colors = ['royalblue', 'darkorange', 'green', 'gray']
    fig = make_subplots(rows=rows, cols=2, subplot_titles=subplot_titles)
    for idx, col in enumerate(plot_cols):
        row = idx // 2 + 1
        col_pos = idx % 2 + 1
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Bar(x=df_ticker.index, y=df_ticker[col], name=col, marker_color=color),
            row=row, col=col_pos
        )
        fig.add_trace(
            go.Scatter(x=df_ticker.index, y=ma[col], mode='lines', name=f'{col} MA(4)', line=dict(color='red')),
            row=row, col=col_pos
        )
    fig.update_layout(
        title_text="Income Statement Overview - " + ticker,
        showlegend=False,
        height=400 * rows,
        width=1200,
        template="plotly_white"
    )
    fig.update_yaxes(ticksuffix="bn")
    return fig

def create_gr_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[(df_temp.TICKER == ticker) & (df_temp.KEYCODE.isin(IS))]
    df_ticker = df_ticker.pivot(index='DATE', columns='KEYCODE', values='YoY')
    df_ticker = df_ticker * 100
    plot_cols = [col for col in ['Net_Revenue', 'Gross_Profit', 'EBIT', 'NPATMI'] if col in df_ticker.columns]
    if not plot_cols:
        return go.Figure()
    ma = df_ticker[plot_cols].rolling(window=4, min_periods=1).mean()
    subplot_titles = [col.replace('_', ' ') for col in plot_cols]
    n = len(plot_cols)
    rows = (n + 1) // 2
    colors = ['royalblue', 'darkorange', 'green', 'gray']
    fig = make_subplots(rows=rows, cols=2, subplot_titles=subplot_titles)
    for idx, col in enumerate(plot_cols):
        row = idx // 2 + 1
        col_pos = idx % 2 + 1
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Bar(x=df_ticker.index, y=df_ticker[col], name=f'{col} Growth', marker_color=color),
            row=row, col=col_pos
        )
        fig.add_trace(
            go.Scatter(x=df_ticker.index, y=ma[col], mode='lines', name=f'{col} MA(4)', line=dict(color='red')),
            row=row, col=col_pos
        )
    fig.update_layout(
        title_text="Income Statement Overview - " + ticker,
        showlegend=False,
        height=400 * rows,
        width=1200,
        template="plotly_white"
    )
    fig.update_yaxes(ticksuffix="%")
    return fig

def create_margin_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[(df_temp.TICKER == ticker) & (df_temp.KEYCODE.isin(MARGIN))]
    df_ticker = df_ticker.pivot(index='DATE', columns='KEYCODE', values='VALUE')
    df_ticker = df_ticker * 100
    plot_cols = [col for col in ['Gross_Margin', 'EBIT_Margin', 'EBITDA_Margin', 'NPAT_Margin'] if col in df_ticker.columns]
    if not plot_cols:
        return go.Figure()
    ma = df_ticker[plot_cols].rolling(window=4, min_periods=1).mean()
    subplot_titles = [col.replace('_', ' ') for col in plot_cols]
    n = len(plot_cols)
    rows = (n + 1) // 2
    colors = ['royalblue', 'darkorange', 'green', 'gray']
    fig = make_subplots(rows=rows, cols=2, subplot_titles=subplot_titles)
    for idx, col in enumerate(plot_cols):
        row = idx // 2 + 1
        col_pos = idx % 2 + 1
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Bar(x=df_ticker.index, y=df_ticker[col], name=col, marker_color=color),
            row=row, col=col_pos
        )
        fig.add_trace(
            go.Scatter(x=df_ticker.index, y=ma[col], mode='lines', name=f'{col} MA(4)', line=dict(color='red')),
            row=row, col=col_pos
        )
    fig.update_layout(
        title_text="Margins Overview - " + ticker,
        showlegend=False,
        height=400 * rows,
        width=1200,
        template="plotly_white"
    )
    fig.update_yaxes(ticksuffix="%")
    return fig

def create_bank_plots(df, ticker: str):
    df_temp = df.copy()
    df_ticker = df_temp[df_temp.TICKER == ticker]
    plot_cols = [col for col in ['PPOP', 'NIM', 'Loan yield', 'NPL (3-5)'] if col in df_ticker.columns]
    if not plot_cols:
       return go.Figure()
    ma = df_ticker[plot_cols].rolling(window=4, min_periods=1).mean()
    subplot_titles = [col.replace('_', ' ') for col in plot_cols]
    n = len(plot_cols)
    rows = (n + 1) // 2
    colors = ['royalblue', 'darkorange', 'green', 'gray']
    fig = make_subplots(rows=rows, cols=2, subplot_titles=subplot_titles)
    for idx, col in enumerate(plot_cols):
       row = idx // 2 + 1
       col_pos = idx % 2 + 1
       color = colors[idx % len(colors)]
       fig.add_trace(
           go.Bar(x=df_ticker.index, y=df_ticker[col], name=col, marker_color=color),
           row=row, col=col_pos
       )
       fig.add_trace(
           go.Scatter(x=df_ticker.index, y=ma[col], mode='lines', name=f'{col} MA(4)', line=dict(color='red')),
           row=row, col=col_pos
       )
    fig.update_layout(
       title_text="Bank Supplement Overview - " + ticker,
       showlegend=False,
       height=400 * rows,
       width=1200,
       template="plotly_white"
    )
    fig.update_yaxes(ticksuffix="bn")
    return fig

# Plot P/E and P/B with dotted line for average and +1 and -1 standard deviation
def create_pe_pb_plot(df, ticker):
    df_temp = df.copy()
    df_ticker = df_temp[df_temp['TICKER'] == ticker]
    pe_data = df_ticker.pivot(index='TRADE_DATE', columns='TICKER', values='P/E')
    pe_data = pe_data.ffill()  # Forward fill to handle missing values
    pb_data = df_ticker.pivot(index='TRADE_DATE', columns='TICKER', values='P/B')
    pb_data = pb_data.ffill()  # Forward fill to handle missing values
    ps_data = df_ticker.pivot(index='TRADE_DATE', columns='TICKER', values='P/S')
    ps_data = ps_data.ffill()  # Forward fill to handle missing values

    # Calculate mean and standard deviation
    pe_mean = pe_data[ticker].mean()
    pe_std = pe_data[ticker].std()
    pb_mean = pb_data[ticker].mean()
    pb_std = pb_data[ticker].std()
    ps_mean = ps_data[ticker].mean()
    ps_std = ps_data[ticker].std()

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=(f"{ticker} P/E Ratio", f"{ticker} P/B Ratio", f"{ticker} P/S Ratio"))

    #fig P/E
    fig.add_trace(go.Scatter(x=pe_data.index, y=pe_data[ticker], mode='lines', name='P/E', line=dict(color='green')),
                  row=1, col=1)
    fig.add_hline(y=pe_mean, line_dash="dash", line_color="red", row=1, col=1, line_width=1)
    fig.add_hline(y=pe_mean + pe_std, line_dash="dash", line_color="grey", row=1, col=1, line_width=1)
    fig.add_hline(y=pe_mean - pe_std, line_dash="dash", line_color="grey", row=1, col=1, line_width=1)
    # fig P/B
    fig.add_trace(go.Scatter(x=pb_data.index, y=pb_data[ticker], mode='lines', name='P/B', line=dict(color='green')),
                  row=2, col=1)
    fig.add_hline(y=pb_mean, line_dash="dash", line_color="red", row=2, col=1, line_width=1)
    fig.add_hline(y=pb_mean + pb_std, line_dash="dash", line_color="grey", row=2, col=1, line_width=1)
    fig.add_hline(y=pb_mean - pb_std, line_dash="dash", line_color="grey", row=2, col=1, line_width=1)
    # fig P/S
    fig.add_trace(go.Scatter(x=ps_data.index, y=ps_data[ticker], mode='lines', name='P/S', line=dict(color='green')),
                  row=3, col=1) 
    fig.add_hline(y=ps_mean, line_dash="dash", line_color="red", row=3, col=1, line_width=1)
    fig.add_hline(y=ps_mean + ps_std, line_dash="dash", line_color="grey", row=3, col=1, line_width=1)
    fig.add_hline(y=ps_mean - ps_std, line_dash="dash", line_color="grey", row=3, col=1, line_width=1)  

    fig.update_layout(height=1200)
    return fig

#%% Extract key data for displays
def extract_key_data(df1, df2, ticker):
    val = df1.copy()
    mcap = df2.copy()
    key_data = {}
    for col in ['P/E', 'P/B', 'EV/EBITDA']:
        vals = val[(val['TICKER'] == ticker)].sort_values('TRADE_DATE', ascending=False)[col]
        vals = pd.to_numeric(vals, errors='coerce')
        latest_val = vals[~vals.isna()].iloc[0] if not vals[~vals.isna()].empty else None
        key_data[col] = latest_val
    mcap_vals = mcap[mcap['TICKER'] == ticker]['CUR_MKT_CAP']
    key_data['M_CAP'] = mcap_vals.iloc[0] if not mcap_vals.empty else None
    return key_data


#%% Streamlit App Design
st.set_page_config(layout = 'wide', page_title="Company Dashboard")

# Title
st.title("Company Dashboard")

# Side bar for ticker selection and start year selection
st.sidebar.header('Ticker Selection')
selected_ticker = st.sidebar.selectbox("Select Ticker", df['TICKER'].unique())
years = sorted(df['YEAR'].unique()) # Add a year selector
start_year = st.sidebar.selectbox("Select Start Year", years, index=2) #defaulted to 2020

# Display selected ticker as header
st.header(f"Data for {selected_ticker}")

# Boxes to display most recent P/E, P/B, EV/EBITDA, and market cap level
key_data = extract_key_data(val,mcap, selected_ticker)
st.subheader("Key Statistics")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Market Cap", f"{key_data['M_CAP']:,.0f}" if key_data['M_CAP'] is not None else "N/A", border = True)
with col2:
    st.metric("P/E Ratio", f"{key_data['P/E']:,.2f}" if key_data['P/E'] is not None else "N/A", border = True)
with col3:
    st.metric("P/B Ratio", f"{key_data['P/B']:,.2f}" if key_data['P/B'] is not None else "N/A", border = True)
with col4:
    st.metric("EV/EBITDA", f"{key_data['EV/EBITDA']:,.2f}" if key_data['EV/EBITDA'] is not None else "N/A", border = True)
with col5:
    # Format the latest TRADE_DATE as 'Mon-Day-Year'
    latest_date = pd.to_datetime(val['TRADE_DATE'].max())
    formatted_date = latest_date.strftime('%b-%d-%Y') if not pd.isnull(latest_date) else "N/A"
    st.metric("Last Data", formatted_date, border=True)

# Filter dataframe based on selected start year
df = df[df['YEAR'] >= start_year]

# Add plots below the tables
fig_FA = create_FA_plots(df, selected_ticker)
fig_GR = create_gr_plots(df, selected_ticker)
fig_MARGIN = create_margin_plots(df, selected_ticker)
fig_BANK_SUPPLEMENT = create_bank_plots(bank, selected_ticker)

# Tab for 3 financial graphs
tab1, tab2, tab3, tab4 = st.tabs(["IS", "Bank", "Growth", "Margin"])
with tab1:
    st.plotly_chart(fig_FA)
with tab2:
    st.plotly_chart(fig_BANK_SUPPLEMENT)
with tab3:
    st.plotly_chart(fig_GR)
with tab4:
    st.plotly_chart(fig_MARGIN)

# Valuation Plots
fig_val = create_pe_pb_plot(val, selected_ticker)
with st.expander("Valuation Ratios", expanded=True):
    st.plotly_chart(fig_val, key="pe_chart")

# Financial Tables:
fs_table_result = create_fs_table_main(df, selected_ticker)
bs_table_result = create_bs_table(df, selected_ticker)
cf_table_result = create_cf_table(df, selected_ticker)

tab1, tab2, tab3 = st.tabs(["Financial Summary", "Balance Sheet", "Cash Flow"])

with tab1:
    st.subheader("Financial Summary Table (IS, Growth, Margin)")
    st.dataframe(fs_table_result)
with tab2:
    st.subheader("Balance Sheet Table")
    st.dataframe(bs_table_result)
with tab3:
    st.subheader("Cash Flow Table")
    st.dataframe(cf_table_result)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
from scipy.interpolate import make_interp_spline
import warnings
from datetime import datetime

# Configure Streamlit page
warnings.filterwarnings('ignore')
st.set_page_config(page_title='Performance Analyser', page_icon=':bar_chart:', layout='wide')

# Title and description
st.title(":bar_chart: John Doe - Account Performance from Sept 2023 - Mar 2024")
st.markdown("""
This dashboard provides a detailed overview of the trading performance for the client from September 2023 to March 2024. 
It includes cumulative balance analysis, net profit per symbol, best trading sessions, and actionable insights.
**Starting Balance : £25,000**.
""")

# Load and preprocess data
file_path = 'FTMO.CSV.REAL.csv'
df = pd.read_csv(file_path)
df['Open'] = pd.to_datetime(df['Open'], format='%d/%m/%Y %H:%M')
df['Close'] = pd.to_datetime(df['Close'], format='%d/%m/%Y %H:%M')
df['Trade duration in minutes'] = df['Trade duration in seconds'] / 60
df.drop(['Trade duration in seconds'], axis=1, inplace=True)
df.sort_values(by='Close', inplace=True)

# Define the trading session function and create the Trading Session column
def get_trading_session(hour):
    if 12 <= hour < 17:
        return 'New York Session'
    elif 7 <= hour < 10:
        return 'London Session'
    else:
        return 'Out of Session'

df['Trading Session'] = df['Close'].dt.hour.apply(get_trading_session)

# Perform the grouping operations after the column is created
net_profit_per_symbol = df.groupby('Symbol')['Profit'].sum().sort_values()
session_performance = df.groupby('Trading Session')['Profit'].sum().sort_values(ascending=False)

# Calculate cumulative balance
initial_balance = 25000
df['Cumulative Profit'] = df['Profit'].cumsum()
df['Balance'] = initial_balance + df['Cumulative Profit']

# Interpolation for smoothing the balance line
x = np.arange(len(df))
y = df['Balance'].values
x_smooth = np.linspace(x.min(), x.max(), 10000)
spl = make_interp_spline(x, y, k=3)
y_smooth = spl(x_smooth)

# Calculate total P&L
total_pnl = df['Profit'].sum()

# Key metrics
total_trades = len(df)
most_traded_instrument = df['Symbol'].mode()[0]
most_traded_day = df['Close'].dt.day_name().mode()[0]

# Calculate win rate
winning_trades = df[df['Profit'] > 0]
win_rate = len(winning_trades) / total_trades * 100 if not winning_trades.empty else None

# Calculate Risk-Reward (RR) Ratio using Average Profit and Average Loss
average_profit = df[df['Profit'] > 0]['Profit'].mean()
average_loss = df[df['Profit'] < 0]['Profit'].mean()
rr_ratio_avg = abs(average_profit / average_loss) if average_loss != 0 else None

# Calculate percentage growth
percentage_growth = (df['Balance'].iloc[-1] - initial_balance) / initial_balance * 100

# Calculate additional key metrics
max_drawdown = df['Balance'].min() - initial_balance
average_trade_duration = df['Trade duration in minutes'].mean()
average_win = df[df['Profit'] > 0]['Profit'].mean()
average_loss = df[df['Profit'] < 0]['Profit'].mean()

# Calculate the profit/loss for trades out of session
out_of_session_trades = df[df['Trading Session'] == 'Out of Session']
out_of_session_loss = out_of_session_trades['Profit'].sum()


# Display the key metrics in a more compact manner
st.markdown("### Key Metrics")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric(label="Total P&L", value=f"+ £{total_pnl:,.2f}")
col2.metric(label="Trades", value=f"{total_trades}")
col3.metric(label="Account Growth", value=f"+{percentage_growth:.2f}%")
if rr_ratio_avg is not None:
    col4.metric(label="Average RRR", value=f"{rr_ratio_avg:.2f}")
if win_rate is not None:
    col5.metric(label="Win Rate", value=f"{win_rate:.2f}%")
col6.metric(label="Most Traded Day", value=f"{most_traded_day}")

main_col, side_col = st.columns([2, 1])

with main_col:
    # Cumulative balance plot
    st.subheader("Account Balance Growth")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x_smooth, y_smooth, color='teal')
    ax.axhline(y=initial_balance, color='gray', linestyle='--')
    ax.set_xlabel('Number of trades')
    ax.set_ylabel('Balance')
    ax.set_title('Cumulative Balance')
    ax.set_xlim(x.min(), x.max())
    ax.grid(False)
    st.pyplot(fig)

    st.subheader("Trading Session Performance")
    # Define colors
    colors = ['green' if session in ['New York Session', 'London Session'] else 'red' for session in session_performance.index]
    fig, ax = plt.subplots(figsize=(5, 3))
    session_performance.plot(kind='bar', ax=ax, color=colors)
    ax.set_ylabel('Net Profit')
    ax.set_xticklabels(session_performance.index, rotation=45, ha='right', fontsize=10)
    ax.grid(True, which='both', axis='y', linestyle='-')  # Only horizontal lines
    st.pyplot(fig)
    plt.show()


# Calculate the profit/loss for trades out of session
out_of_session_trades = df[df['Trading Session'] == 'Out of Session']
out_of_session_loss = out_of_session_trades['Profit'].sum()

# Identify the worst trading pair and session
worst_trading_pair = net_profit_per_symbol.idxmin()
worst_trading_pair_loss = net_profit_per_symbol.min()
worst_trading_session = session_performance.idxmin()
worst_trading_session_loss = session_performance.min()


with side_col:
    st.subheader("Insights and Advice")
    st.markdown(f"""
- **Best Trading Pair**: **{net_profit_per_symbol.idxmax()}** with a net profit of £{net_profit_per_symbol.max():,.2f}.
- **Worst Trading Pair**: **{worst_trading_pair}** with a net loss of £{abs(worst_trading_pair_loss):,.2f}.
- **Best Trading Session**: **{session_performance.idxmax()}** with a total profit of £{session_performance.max():,.2f}.
- **Worst Trading Session**: **{worst_trading_session}** with a total loss of £{abs(worst_trading_session_loss):,.2f}.
- **Advice**:
  - :chart_with_upwards_trend: **Focus on trading the {net_profit_per_symbol.idxmax()} pair** for highest returns.
  - :mag_right: **Review and refine strategies** for pairs and sessions with lower performance.
  - :pound: Aim for at least **2 RR Ratio** and **50% win rate** to enhance profitability.
  - :clock1: **Consider only trading LDN and NY sessions** - trading out of session proves to be a hindrance to being profitable.
  - :no_entry_sign: **If you stayed away from trading 'Out of Session', you would've prevented the loss of: £{out_of_session_loss:,.2f}.**
""")
    


    st.subheader("Other Key Metrics")
    st.markdown(f"""
    - **Most Traded Pair**: **{most_traded_instrument}**
    - **Average Trade Duration**: **{average_trade_duration:.2f} mins**
    - **Max Drawdown**: **£{max_drawdown:,.2f}**
    - **Average Win**: **£{average_win:.2f}**
    - **Average Loss**: **£{average_loss:.2f}**
    """)

# Additional analysis below the main chart
st.markdown("### Additional Analysis")
col7, col8 = st.columns(2)

with col7:    
    st.subheader("Trade Duration Analysis")
    trade_duration = df['Trade duration in minutes']
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(trade_duration, bins=30, color='skyblue', edgecolor='black')
    ax.set_xlabel('Duration (minutes)')
    ax.set_ylabel('Frequency')
    ax.set_title('Trade Durations')
    st.pyplot(fig)

with col8:
    st.subheader("Net Profit per Symbol")
    fig, ax = plt.subplots(figsize=(6, 4))
    net_profit_per_symbol.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_ylabel('Net Profit')
    ax.set_xticklabels(net_profit_per_symbol.index, rotation=45, ha='right', fontsize=10)
    ax.grid(True, which='both', axis='y', linestyle='-')  # Only horizontal lines
    st.pyplot(fig)
    plt.show()

# Summary and conclusion
st.markdown("""
### Summary
- **Total Profit and Loss (P&L)**: The account has a cumulative profit of £3,255.22.
- **Cumulative Balance**: The balance has shown steady growth over the period with occasional drawdowns.
- **Net Profit per Symbol**: The performance varies across different symbols, highlighting areas of strength and weakness.
- **Trading Session Performance**: The NY session has been the most profitable, followed by the LDN session.

This detailed report helps in understanding the trading performance, identifying profitable strategies, and areas that need improvement.
""")


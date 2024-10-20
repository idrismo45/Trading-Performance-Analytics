

# Performance Analyser Code Explanation

This document provides an in-depth explanation of the **Performance Analyser** application, which analyses a client's trading performance from September 2023 to March 2024. The application utilizes **Streamlit** for the dashboard interface, **Matplotlib** and **Plotly** for visualizations, and **Pandas** for data manipulation. Below is a detailed line-by-line explanation of the code.

## Table of Contents
1. [Importing Libraries](#importing-libraries)
2. [Streamlit Page Configuration](#streamlit-page-configuration)
3. [Title and Description](#title-and-description)
4. [Loading and Preprocessing Data](#loading-and-preprocessing-data)
5. [Defining Trading Sessions](#defining-trading-sessions)
6. [Grouping and Calculating Metrics](#grouping-and-calculating-metrics)
7. [Smoothing the Balance Line](#smoothing-the-balance-line)
8. [Key Metrics Calculation](#key-metrics-calculation)
9. [Additional Metrics Calculation](#additional-metrics-calculation)
10. [Displaying Key Metrics](#displaying-key-metrics)
11. [Visualizations](#visualizations)
12. [Insights and Advice](#insights-and-advice)

## Importing Libraries

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
from scipy.interpolate import make_interp_spline
import warnings
from datetime import datetime
```

- **streamlit**: For creating interactive web applications.
- **pandas**: For data manipulation and analysis.
- **matplotlib**: For plotting and visualizing data.
- **numpy**: For numerical computations.
- **plotly.graph_objs**: For creating interactive plots (optional).
- **scipy.interpolate**: For smoothing the cumulative balance line.
- **warnings**: To manage warnings.
- **datetime**: For handling date and time data.

## Streamlit Page Configuration

```python
warnings.filterwarnings('ignore')
st.set_page_config(page_title='Performance Analyser', page_icon=':bar_chart:', layout='wide')
```

- **warnings.filterwarnings('ignore')**: Suppresses warnings for a cleaner UI.
- **st.set_page_config**: Sets the title, icon, and layout of the Streamlit page.

## Title and Description

```python
st.title(":bar_chart: John Doe - Account Performance from Sept 2023 - Mar 2024")
st.markdown("""
This dashboard provides a detailed overview of the trading performance for the client from September 2023 to March 2024. 
It includes cumulative balance analysis, net profit per symbol, best trading sessions, and actionable insights.
**Starting Balance : £25,000**.
""")
```

- **st.title**: Displays the main title of the application.
- **st.markdown**: Formats rich text for a description of the dashboard and the starting balance.

## Loading and Preprocessing Data

```python
file_path = 'FTMO.CSV.REAL.csv'
df = pd.read_csv(file_path)
df['Open'] = pd.to_datetime(df['Open'], format='%d/%m/%Y %H:%M')
df['Close'] = pd.to_datetime(df['Close'], format='%d/%m/%Y %H:%M')
df['Trade duration in minutes'] = df['Trade duration in seconds'] / 60
df.drop(['Trade duration in seconds'], axis=1, inplace=True)
df.sort_values(by='Close', inplace=True)
```

- **file_path**: Path to the CSV file containing trading data.
- **pd.read_csv**: Loads the CSV data into a DataFrame.
- **pd.to_datetime**: Converts the 'Open' and 'Close' columns to datetime objects.
- **Trade duration calculation**: Computes trade duration in minutes and drops the original column.
- **Sorting**: Organizes data chronologically by the 'Close' column.

## Defining Trading Sessions

```python
def get_trading_session(hour):
    if 12 <= hour < 17:
        return 'New York Session'
    elif 7 <= hour < 10:
        return 'London Session'
    else:
        return 'Out of Session'

df['Trading Session'] = df['Close'].dt.hour.apply(get_trading_session)
```

- **get_trading_session**: Classifies trades into 'New York', 'London', or 'Out of Session'.
- **apply**: Applies the function to each hour in the 'Close' column.

## Grouping and Calculating Metrics

```python
net_profit_per_symbol = df.groupby('Symbol')['Profit'].sum().sort_values()
session_performance = df.groupby('Trading Session')['Profit'].sum().sort_values(ascending=False)

# Calculate cumulative balance
initial_balance = 25000
df['Cumulative Profit'] = df['Profit'].cumsum()
df['Balance'] = initial_balance + df['Cumulative Profit']
```

- **groupby**: Groups data by 'Symbol' and 'Trading Session' for profit calculation.
- **cumsum**: Computes cumulative profit and overall balance based on the initial balance of £25,000.

## Smoothing the Balance Line

```python
x = np.arange(len(df))
y = df['Balance'].values
x_smooth = np.linspace(x.min(), x.max(), 10000)
spl = make_interp_spline(x, y, k=3)
y_smooth = spl(x_smooth)
```

- **np.arange**: Creates an array of indices.
- **np.linspace**: Generates smooth x values for plotting.
- **make_interp_spline**: Smooths the balance line for visualization.

## Key Metrics Calculation

```python
total_pnl = df['Profit'].sum()
total_trades = len(df)
most_traded_instrument = df['Symbol'].mode()[0]
most_traded_day = df['Close'].dt.day_name().mode()[0]

# Calculate win rate
winning_trades = df[df['Profit'] > 0]
win_rate = len(winning_trades) / total_trades * 100 if not winning_trades.empty else None

# Calculate Risk-Reward (RR) Ratio
average_profit = df[df['Profit'] > 0]['Profit'].mean()
average_loss = df[df['Profit'] < 0]['Profit'].mean()
rr_ratio_avg = abs(average_profit / average_loss) if average_loss != 0 else None

# Calculate percentage growth
percentage_growth = (df['Balance'].iloc[-1] - initial_balance) / initial_balance * 100
```

- Calculates key metrics: total profit/loss, total trades, most traded instrument, most traded day, win rate, risk-reward ratio, and percentage growth.

## Additional Metrics Calculation

```python
max_drawdown = df['Balance'].min() - initial_balance
average_trade_duration = df['Trade duration in minutes'].mean()
average_win = df[df['Profit'] > 0]['Profit'].mean()
average_loss = df[df['Profit'] < 0]['Profit'].mean()
```

- Computes additional metrics: maximum drawdown, average trade duration, average win, and average loss.

## Displaying Key Metrics

```python
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
```

- Displays key metrics using Streamlit’s `metric` function for an overview of trading performance.

## Visualizations

### Cumulative Balance Plot

```python
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x_smooth, y_smooth, color='teal')
ax.axhline(y=initial_balance, color='gray', linestyle='--')
ax.set_xlabel('Number of trades')
ax.set_ylabel('Balance')
ax.set_title('Cumulative Balance')
ax.set_xlim(x.min(), x.max())
ax.grid(False)
st.pyplot(fig)
```

- Uses Matplotlib to create a cumulative balance plot for visual performance analysis.

### Trading Session Performance Bar Chart

```python
colors = ['green' if session in ['New York Session', 'London Session'] else 'red' for session in session_performance.index]
fig, ax = plt.subplots(figsize=(5, 3))
session_performance.plot(kind='bar', ax=ax, color=colors)
ax.set_ylabel('Net Profit')
ax.set_xticklabels(session_performance.index, rotation=45, ha='right', fontsize=10)
ax.grid(True, which='both', axis='y', linestyle='-')  # Only horizontal lines
st.pyplot(fig)
plt.show()
```

- Creates a bar chart to visualize net profit per trading session, distinguishing profitable and unprofitable sessions with color coding.

## Insights and Advice

```python
st.subheader("Insights and Advice")
st.markdown(f"""
- **Best Trading Pair**: **{net_profit

_per_symbol.idxmax()}** with profit of £{net_profit_per_symbol.max():.2f}
- **Worst Trading Pair**: **{net_profit_per_symbol.idxmin()}** with loss of £{net_profit_per_symbol.min():.2f}
- Consider focusing on trading pairs that yield higher profits and limiting exposure to those with losses.
""")
```

- Summarizes key insights based on the analysis, providing actionable advice for future trading.

---

## Conclusion
This dashboard serves as a comprehensive tool for traders to evaluate their performance over a specific period, offering valuable insights and metrics to guide their trading strategies. The use of visualizations enhances understanding, making it easier for traders to assess their results and make informed decisions moving forward.

---

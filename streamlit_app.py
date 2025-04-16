import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


# Download DXY data
dxy = yf.download("DX-Y.NYB", start="2023-01-01", end="2025-04-15")
dxy = dxy[['Close']]  # Keep only closing price
dxy = dxy.reset_index()
dxy.rename(columns={"Date": "Date", "Close": "DXY"}, inplace=True)

# Save to CSV
dxy.to_csv("dxy_data.csv", index=False)

print("✅ DXY data saved to dxy_data.csv")


st.set_page_config(layout="wide")
st.title("US Dollar Index vs 10-Year Treasury Yield")

# --- Load and clean DXY data ---
dxy_df = pd.read_csv("dxy_data.csv")
# Adjust the column name based on what the CSV actually uses
dxy_df.rename(columns={"observation_date": "Date"}, inplace=True)

dxy_df['Date'] = pd.to_datetime(dxy_df['Date'])
dxy_df['DXY'] = pd.to_numeric(dxy_df['DXY'].astype(str).str.replace(',', ''), errors='coerce')
dxy_df = dxy_df[['Date', 'DXY']].rename(columns={'DXY': 'DXY'})
dxy_df = dxy_df.sort_values('Date')

# --- Load and clean Yield data ---
yield_df = pd.read_csv("dgs10_data.csv")
yield_df.rename(columns={"observation_date": "Date"}, inplace=True)
yield_df['Date'] = pd.to_datetime(yield_df['Date'])
yield_df['DGS10'] = pd.to_numeric(yield_df['DGS10'].astype(str).str.replace(',', ''), errors='coerce')
yield_df = yield_df[['Date', 'DGS10']].rename(columns={'DGS10': 'Yield'})
yield_df = yield_df.sort_values('Date')

# Drop rows where 'Date' is missing
dxy_df = dxy_df.dropna(subset=["Date"])
yield_df = yield_df.dropna(subset=["Date"])

# --- Merge the two datasets on nearest previous dates ---
merged_df = pd.merge_asof(dxy_df, yield_df, on='Date')
merged_df.dropna(inplace=True)

# --- Show preview of merged data ---
st.write("📊 Preview of merged data:", merged_df.head())


# --- Plotting ---
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot DXY (left axis)
ax1.plot(merged_df['Date'], merged_df['DXY'], color="crimson", label="US Dollar Index (scaled)", linewidth=2)
ax1.set_ylim(100, 110)
ax1.set_xlabel("Date")
ax1.set_ylabel("US Dollar Index", color="crimson")
ax1.tick_params(axis='y', labelcolor='crimson')


# Plot 10Y Yield (right axis)
ax2 = ax1.twinx()
ax2.set_ylabel("10-Year Yield (%)", color="navy")
ax2.plot(merged_df['Date'], merged_df['Yield'], color="navy", label="10Y Yield")
ax2.tick_params(axis='y', labelcolor='navy')
ax2.set_ylim(3.4, 5)

# Optional: add 'liberation day' line (e.g. March 2025)
ax1.axvline(pd.to_datetime("2025-03-01"), color="black", linestyle="dotted", label="‘Liberation Day’")

fig.tight_layout()
st.pyplot(fig)
import pandas as pd

# Load fact and account dimension
fact = pd.read_csv("../data/raw/Fact_Financials.csv")
dim_account = pd.read_csv("../data/raw/Dim_Account.csv")

# Merge to get Statement_Section (Revenue, COGS, OPEX)
df = fact.merge(dim_account, on="Account_ID", how="left")

# Group by Date, Scenario, and Statement Section
monthly_summary = (
    df.groupby(["Date", "Scenario", "Statement_Section"])["Amount"]
    .sum()
    .unstack(level=["Scenario", "Statement_Section"])
)

# Format as currency in thousands ($K) for quick readability
summary_k = (monthly_summary / 1000).round(1)

print("=== MONTHLY TOTALS ($ in Thousands) ===")
print(summary_k)

print("\n=== OVERALL MONTHLY MIN / MAX RANGES (Actuals) ===")
actual_df = (
    df[df["Scenario"] == "Actual"]
    .groupby(["Date", "Statement_Section"])["Amount"]
    .sum()
    .unstack()
)
for col in ["Revenue", "COGS", "OPEX"]:
    min_val = actual_df[col].min()
    max_val = actual_df[col].max()
    print(f"{col:8s} -> Min: ${min_val:,.2f} | Max: ${max_val:,.2f}")

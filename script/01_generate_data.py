import os
import itertools
import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Ensure output directories exist
os.makedirs("../data/raw", exist_ok=True)

# -------------------------------------------------------------
# 1. DIMENSION: ACCOUNTS
# -------------------------------------------------------------
accounts_data = [
    # Statement Section, Category, Account_ID, Account_Name
    ("Revenue", "Subscription", "REV_101", "Enterprise SaaS Subscription"),
    ("Revenue", "Subscription", "REV_102", "Mid-Market SaaS Subscription"),
    ("Revenue", "Services", "REV_201", "Implementation & Consulting Services"),
    ("COGS", "Hosting & Infra", "COG_101", "Production Cloud Hosting"),
    ("COGS", "Direct Labor", "COG_201", "Professional Services Delivery Salaries"),
    ("OPEX", "Payroll", "OPX_101", "Salaries & Benefits - R&D"),
    ("OPEX", "Payroll", "OPX_102", "Salaries & Benefits - Sales & Marketing"),
    ("OPEX", "Payroll", "OPX_103", "Salaries & Benefits - G&A"),
    ("OPEX", "Marketing & Sales", "OPX_201", "Performance Advertising & Demand Gen"),
    ("OPEX", "Marketing & Sales", "OPX_202", "Events, Sponsorships & Travel"),
    ("OPEX", "Technology & R&D", "OPX_301", "R&D Cloud Testing & Staging Compute"),
    ("OPEX", "Technology & R&D", "OPX_302", "Internal Software Licenses & Tools"),
    ("OPEX", "General & Admin", "OPX_401", "Legal, Audit & Professional Fees"),
    ("OPEX", "General & Admin", "OPX_402", "Office Rent & Facilities"),
]

dim_account = pd.DataFrame(
    accounts_data,
    columns=["Statement_Section", "Category", "Account_ID", "Account_Name"],
)

# -------------------------------------------------------------
# 2. DIMENSION: DEPARTMENTS / COST CENTRES
# -------------------------------------------------------------
departments_data = [
    # Department_ID, Department_Name, Cost_Center_Owner
    ("D10", "Commercial Sales", "VP of Sales"),
    ("D20", "Marketing", "Chief Marketing Officer"),
    ("D30", "Research & Development", "Chief Technology Officer"),
    ("D40", "Professional Services", "VP of Services"),
    ("D50", "General & Administrative", "Chief Financial Officer"),
]

dim_department = pd.DataFrame(
    departments_data, columns=["Department_ID", "Department_Name", "Cost_Center_Owner"]
)

# Account to Department standard mapping
account_dept_map = {
    "REV_101": "D10",
    "REV_102": "D10",
    "REV_201": "D40",
    "COG_101": "D30",
    "COG_201": "D40",
    "OPX_101": "D30",
    "OPX_102": "D10",
    "OPX_103": "D50",
    "OPX_201": "D20",
    "OPX_202": "D20",
    "OPX_301": "D30",
    "OPX_302": "D30",
    "OPX_401": "D50",
    "OPX_402": "D50",
}

# -------------------------------------------------------------
# 3. FACT: FINANCIAL TRANSACTIONS (Monthly Budget & Actuals for 2025)
# -------------------------------------------------------------
dates = pd.date_range(start="2025-01-01", end="2025-12-01", freq="MS")

# Monthly baseline budget amounts ($)
base_budget = {
    "REV_101": 550000,  # Enterprise SaaS
    "REV_102": 280000,  # Mid-Market SaaS
    "REV_201": 140000,  # Implementation Services
    "COG_101": 75000,  # Prod Cloud
    "COG_201": 80000,  # Services Salaries
    "OPX_101": 210000,  # R&D Salaries
    "OPX_102": 180000,  # Sales Salaries
    "OPX_103": 95000,  # G&A Salaries
    "OPX_201": 85000,  # Digital Ad Spend
    "OPX_202": 35000,  # Travel & Events
    "OPX_301": 45000,  # R&D Compute / Staging
    "OPX_302": 25000,  # Software Tools
    "OPX_401": 30000,  # Legal & Audit
    "OPX_402": 20000,  # Facilities
}

records = []

for dt in dates:
    month_num = dt.month
    date_str = dt.strftime("%Y-%m-%d")

    # Seasonality/organic growth ramp (approx 2% MoM growth in Budgeted Revenue)
    growth_multiplier = 1.0 + (0.02 * (month_num - 1))

    for acc_id, base_val in base_budget.items():
        dept_id = account_dept_map[acc_id]

        # 1. Calculate Budget (clean, steady planning baseline)
        if acc_id.startswith("REV"):
            budget_amt = round(base_val * growth_multiplier, 2)
        else:
            budget_amt = round(base_val * (1.0 + (0.008 * (month_num - 1))), 2)

        records.append(
            {
                "Date": date_str,
                "Account_ID": acc_id,
                "Department_ID": dept_id,
                "Scenario": "Budget",
                "Amount": budget_amt,
            }
        )

        # 2. Calculate Actuals (incorporating realistic variance + business stories)
        # Normal fluctuation: +/- 3% to 6%
        fluctuation = np.random.normal(loc=1.0, scale=0.035)
        actual_amt = budget_amt * fluctuation

        # --- STORY INJECTIONS ---

        # Story 1: R&D Cloud Spike (OPX_301) in Q2 & Q3 (Months 5 to 9)
        if acc_id == "OPX_301" and 5 <= month_num <= 9:
            actual_amt = budget_amt * np.random.uniform(
                1.35, 1.55
            )  # 35-55% budget overrun

        # Story 2: Aggressive Marketing Campaign Overrun (OPX_201) in Q1/Q2 (Months 2 to 5)
        # Followed by flat enterprise revenue pickup
        if acc_id == "OPX_201" and 2 <= month_num <= 5:
            actual_amt = budget_amt * np.random.uniform(1.25, 1.40)  # Overspend on ads

        # Story 3: Consulting Services Revenue Dip (REV_201) in Q3 (Months 7 to 9)
        if acc_id == "REV_201" and 7 <= month_num <= 9:
            actual_amt = budget_amt * np.random.uniform(
                0.78, 0.85
            )  # Misses revenue target

        # Realistic data issue: One unexpected legal fee shock in month 8 for G&A (OPX_401)
        if acc_id == "OPX_401" and month_num == 8:
            actual_amt = budget_amt + 42000.0  # One-time IP legal dispute

        records.append(
            {
                "Date": date_str,
                "Account_ID": acc_id,
                "Department_ID": dept_id,
                "Scenario": "Actual",
                "Amount": round(actual_amt, 2),
            }
        )

fact_financials = pd.DataFrame(records)

# -------------------------------------------------------------
# 4. SAVE TO RAW FILES
# -------------------------------------------------------------
dim_account.to_csv("../data/raw/Dim_Account.csv", index=False)
dim_department.to_csv("../data/raw/Dim_Department.csv", index=False)
fact_financials.to_csv("../data/raw/Fact_Financials.csv", index=False)

print(f"Data Generation Complete!")
print(f"Dim_Account records: {len(dim_account)}")
print(f"Dim_Department records: {len(dim_department)}")
print(f"Fact_Financials records: {len(fact_financials)}")

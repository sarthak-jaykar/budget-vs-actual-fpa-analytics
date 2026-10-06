\# DAX Measures Catalog — Nexus Cloud Solutions FP\&A



All DAX business logic is stored within the `\\\_Measures` container table.



\## 1. Baseline Calculations

```dax

Actual Amount = SUM(Fact\\\_Financials\\\[Amount]) -- filtered for Actual scenario

Budget Amount = SUM(Fact\\\_Financials\\\[Amount]) -- filtered for Budget scenario

2. P\\\&L Statement \\\& Margin Performance Measures
Actual Revenue = 

CALCULATE(

\&#x20;   \\\[Actual Amount], 

\&#x20;   Dim\\\_Account\\\[Statement\\\_Section] = "Revenue"

)



Budget Revenue = 

CALCULATE(

\&#x20;   \\\[Budget Amount], 

\&#x20;   Dim\\\_Account\\\[Statement\\\_Section] = "Revenue"

)



Actual COGS = 

CALCULATE(

\&#x20;   \\\[Actual Amount], 

\&#x20;   Dim\\\_Account\\\[Statement\\\_Section] = "COGS"

)



Budget COGS = 

CALCULATE(

\&#x20;   \\\[Budget Amount], 

\&#x20;   Dim\\\_Account\\\[Statement\\\_Section] = "COGS"

)



Actual Gross Profit = \\\[Actual Revenue] - \\\[Actual COGS]



Budget Gross Profit = \\\[Budget Revenue] - \\\[Budget COGS]



Actual Gross Margin % = 

DIVIDE(\\\[Actual Gross Profit], \\\[Actual Revenue], 0)



Budget Gross Margin % = 

DIVIDE(\\\[Budget Gross Profit], \\\[Budget Revenue], 0)



Actual OPEX = 

CALCULATE(

\&#x20;   \\\[Actual Amount], 

\&#x20;   Dim\\\_Account\\\[Statement\\\_Section] = "OPEX"

)



Budget OPEX = 

CALCULATE(

\&#x20;   \\\[Budget Amount], 

\&#x20;   Dim\\\_Account\\\[Statement\\\_Section] = "OPEX"

)



Actual EBITDA = \\\[Actual Gross Profit] - \\\[Actual OPEX]



Budget EBITDA = \\\[Budget Gross Profit] - \\\[Budget OPEX]



Actual EBITDA Margin % = 

DIVIDE(\\\[Actual EBITDA], \\\[Actual Revenue], 0)



Budget EBITDA Margin % = 

DIVIDE(\\\[Budget EBITDA], \\\[Budget Revenue], 0)

3. Financial Variance Analytics

(Standard FP\\\&A Accounting Directionality: Favorable is positive, unfavorable is negative)
Revenue Variance $ = \\\[Actual Revenue] - \\\[Budget Revenue]



Revenue Variance % = 

DIVIDE(\\\[Revenue Variance $], \\\[Budget Revenue], 0)



OPEX Variance $ = \\\[Budget OPEX] - \\\[Actual OPEX]



OPEX Variance % = 

DIVIDE(\\\[Actual OPEX] - \\\[Budget OPEX], \\\[Budget OPEX], 0)



EBITDA Variance $ = \\\[Actual EBITDA] - \\\[Budget EBITDA]



EBITDA Variance % = 

DIVIDE(\\\[EBITDA Variance $], \\\[Budget EBITDA], 0)



Total Net Variance $ = 

VAR RevVar  = \\\[Actual Revenue] - \\\[Budget Revenue]

VAR CogsVar = \\\[Budget COGS] - \\\[Actual COGS]

VAR OpexVar = \\\[Budget OPEX] - \\\[Actual OPEX]

RETURN

RevVar + CogsVar + OpexVar

4. Modeling, Governance \\\& Scaffolding Measures
OPEX Budget Utilization % = 

DIVIDE(\\\[Actual OPEX], \\\[Budget OPEX], 0)



Variance Severity Status = 

VAR RevDiff = \\\[Actual Revenue] - \\\[Budget Revenue]

VAR ExpDiff = (\\\[Actual OPEX] + \\\[Actual COGS]) - (\\\[Budget OPEX] + \\\[Budget COGS])

VAR IsOpexOrCogs = NOT(ISBLANK(\\\[Actual OPEX])) || NOT(ISBLANK(\\\[Actual COGS]))

RETURN

SWITCH(

\&#x20;   TRUE(),

\&#x20;   IsOpexOrCogs \\\&\\\& ExpDiff > 50000, "Critical Overspend",

\&#x20;   IsOpexOrCogs \\\&\\\& ExpDiff > 15000, "Moderate Overrun",

\&#x20;   NOT(IsOpexOrCogs) \\\&\\\& RevDiff < -50000, "Major Revenue Miss",

\&#x20;   "On Track / Normal"

)



Bridge Value = 

SWITCH(

\&#x20;   SELECTEDVALUE(Bridge\\\_Structure\\\[Sort]),

\&#x20;   1, \\\[Budget EBITDA],

\&#x20;   2, \\\[Revenue Variance $],     3, \\\[Budget COGS] - \\\[Actual COGS],     4, \\\[OPEX Variance$],

\&#x20;   5, \\\[Actual EBITDA]

)





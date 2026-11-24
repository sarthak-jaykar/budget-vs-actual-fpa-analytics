# DAX Measures Reference — Nexus Cloud Solutions FP&A

All business measures are stored in the `_Measures` table. The measures below use a consistent financial variance convention:

**Favourable variance is positive; unfavourable variance is negative.**

- Revenue variance: Actual − Budget
- Expense variance (COGS and OPEX): Budget − Actual
- EBITDA variance: Actual − Budget

---

## 1. Baseline Measures

### Actual Amount

```dax
Actual Amount = SUM ( Fact_Financials[Amount] )
```

Base amount measure; the Actual scenario is applied through the model's scenario filter context.

### Budget Amount

```dax
Budget Amount = SUM ( Fact_Financials[Amount] )
```

Base amount measure; the Budget scenario is applied through the model's scenario filter context.

---

## 2. P&L and Margin Measures

```dax
Actual Revenue =
CALCULATE (
    [Actual Amount],
    Dim_Account[Statement_Section] = "Revenue"
)

Budget Revenue =
CALCULATE (
    [Budget Amount],
    Dim_Account[Statement_Section] = "Revenue"
)

Actual COGS =
CALCULATE (
    [Actual Amount],
    Dim_Account[Statement_Section] = "COGS"
)

Budget COGS =
CALCULATE (
    [Budget Amount],
    Dim_Account[Statement_Section] = "COGS"
)

Actual Gross Profit = [Actual Revenue] - [Actual COGS]
Budget Gross Profit = [Budget Revenue] - [Budget COGS]

Actual Gross Margin % =
DIVIDE ( [Actual Gross Profit], [Actual Revenue], 0 )

Budget Gross Margin % =
DIVIDE ( [Budget Gross Profit], [Budget Revenue], 0 )

Actual OPEX =
CALCULATE (
    [Actual Amount],
    Dim_Account[Statement_Section] = "OPEX"
)

Budget OPEX =
CALCULATE (
    [Budget Amount],
    Dim_Account[Statement_Section] = "OPEX"
)

Actual EBITDA = [Actual Gross Profit] - [Actual OPEX]
Budget EBITDA = [Budget Gross Profit] - [Budget OPEX]

Actual EBITDA Margin % =
DIVIDE ( [Actual EBITDA], [Actual Revenue], 0 )

Budget EBITDA Margin % =
DIVIDE ( [Budget EBITDA], [Budget Revenue], 0 )
```

---

## 3. Financial Variance Measures

### Revenue Variance

```dax
Revenue Variance $ = [Actual Revenue] - [Budget Revenue]

Revenue Variance % =
DIVIDE ( [Revenue Variance $], [Budget Revenue], 0 )
```

Positive values indicate revenue above budget.

### COGS Variance

```dax
COGS Variance $ = [Budget COGS] - [Actual COGS]
```

Positive values indicate COGS below budget.

### OPEX Variance

```dax
OPEX Variance $ = [Budget OPEX] - [Actual OPEX]

OPEX Variance % =
DIVIDE ( [OPEX Variance $], [Budget OPEX], 0 )
```

Positive values indicate OPEX below budget; negative values indicate overspend. The percentage uses the same favourable-positive direction as the dollar variance.

### EBITDA Variance

```dax
EBITDA Variance $ = [Actual EBITDA] - [Budget EBITDA]

EBITDA Variance % =
DIVIDE ( [EBITDA Variance $], [Budget EBITDA], 0 )
```

Positive values indicate EBITDA above budget.

### Total Net Variance

```dax
Total Net Variance $ =
VAR RevVar = [Actual Revenue] - [Budget Revenue]
VAR CogsVar = [Budget COGS] - [Actual COGS]
VAR OpexVar = [Budget OPEX] - [Actual OPEX]
RETURN
    RevVar + CogsVar + OpexVar
```

Revenue, COGS and OPEX contributions combined using the favourable-positive convention. Under the project's EBITDA definition, this reconciles to EBITDA Variance $.

---

## 4. Budget Utilisation and Variance Status

### OPEX Budget Utilization %

```dax
OPEX Budget Utilization % =
DIVIDE ( [Actual OPEX], [Budget OPEX], 0 )
```

Share of the OPEX budget consumed by actual expenditure.

### Variance Severity Status

```dax
Variance Severity Status =
VAR RevDiff = [Actual Revenue] - [Budget Revenue]
VAR ExpDiff =
    ( [Actual OPEX] + [Actual COGS] )
        - ( [Budget OPEX] + [Budget COGS] )
VAR IsOpexOrCogs =
    NOT ( ISBLANK ( [Actual OPEX] ) )
        || NOT ( ISBLANK ( [Actual COGS] ) )
RETURN
    SWITCH (
        TRUE (),
        IsOpexOrCogs && ExpDiff > 50000, "Critical Overspend",
        IsOpexOrCogs && ExpDiff > 15000, "Moderate Overrun",
        NOT ( IsOpexOrCogs ) && RevDiff < -50000, "Major Revenue Miss",
        "On Track / Normal"
    )
```

Classifies material expense overruns and revenue shortfalls using the project's stated thresholds.

---

## 5. EBITDA Bridge

### Bridge Value

```dax
Bridge Value =
SWITCH (
    SELECTEDVALUE ( Bridge_Structure[Sort] ),
    1, [Budget EBITDA],
    2, [Revenue Variance $],
    3, [Budget COGS] - [Actual COGS],
    4, [OPEX Variance $],
    5, [Actual EBITDA]
)
```

Returns the value associated with each bridge step: Budget EBITDA, revenue variance, COGS variance, OPEX variance and Actual EBITDA. The OPEX step references the defined measure name `[OPEX Variance $]`.

---

## Measure Design Notes

- `Actual Amount` and `Budget Amount` are base measures; scenario context is supplied by the model.
- Variance measures use one consistent favourable-positive convention.
- `DIVIDE()` is used for ratio calculations to handle zero denominators.
- EBITDA is defined in this project as Gross Profit less OPEX; depreciation and amortisation are not included in the dataset.
- Thresholds in `Variance Severity Status` are project assumptions, not company policy.

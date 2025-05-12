import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import os

# Load dataset
df = pd.read_csv("AIDS_Data_Final.csv")

# Identify share and price columns
share_cols = [col for col in df.columns if col.endswith("_w")]
price_cols = [col for col in df.columns if col.endswith("_lr")]


# Create output folder
output_dir = "aids_results"
os.makedirs(output_dir, exist_ok=True)

# Loop through each sector to drop
for drop_sector in share_cols:
    shares_used = [col for col in share_cols if col != drop_sector]

    # Prepare independent variables (log prices + portfolio value)
    exog_vars = price_cols + ['portfolio_value_ln']
    X = sm.add_constant(df[exog_vars])

    # Run OLS for each share equation (excluding dropped sector)
    results = {}
    adf_results = []

    for share in shares_used:
        y = df[share]
        model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
        results[share] = model

        # ADF test on residuals
        resid = model.resid
        adf_stat, p_val, _, _, crit_vals, _ = adfuller(resid)
        adf_results.append({
            "Dropped": drop_sector,
            "Sector": share,
            "ADF Statistic": adf_stat,
            "p-value": p_val,
            "Stationary": p_val < 0.05,
            "1%": crit_vals['1%'],
            "5%": crit_vals['5%'],
            "10%": crit_vals['10%']
        })

    # Compute elasticities
    def compute_elasticities(results, share_cols, price_cols, df, drop_sector):
        elasticities = pd.DataFrame(index=share_cols, columns=price_cols)
        avg_shares = df[share_cols].mean()
        avg_prices = df[price_cols].mean()

        for share in results:
            gamma = results[share].params
            for price in price_cols:
                elasticity = gamma[price] * avg_prices[price] / avg_shares[share]
                elasticities.loc[share, price] = elasticity

        # Enforce adding-up for dropped sector
        elasticities.loc[drop_sector] = -elasticities.drop(drop_sector).sum(axis=0)

        return elasticities

    elasticities = compute_elasticities(results, share_cols, exog_vars, df, drop_sector)

    # Save elasticities
    elasticities_file = os.path.join(output_dir, f"elasticities_dropped_{drop_sector}.csv")
    elasticities.to_csv(elasticities_file)

    # Save model stats
    model_stats = []
    for share, model in results.items():
        for param, pval in model.pvalues.items():
            model_stats.append({
                "Dropped": drop_sector,
                "Sector": share,
                "Parameter": param,
                "R-squared": model.rsquared,
                "P-value": pval
            })

    model_stats_df = pd.DataFrame(model_stats)
    stats_file = os.path.join(output_dir, f"model_stats_dropped_{drop_sector}.csv")
    model_stats_df.to_csv(stats_file, index=False)

    # Save ADF test results
    adf_results_df = pd.DataFrame(adf_results)
    adf_file = os.path.join(output_dir, f"adf_residuals_dropped_{drop_sector}.csv")
    adf_results_df.to_csv(adf_file, index=False)

    print(f"Finished processing with dropped sector: {drop_sector}")

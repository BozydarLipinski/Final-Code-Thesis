import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import het_breuschpagan
import os
from sklearn.metrics import mean_squared_error

# Load dataset
df = pd.read_csv("AIDS_Data_Final.csv")

# Identify share and price columns
share_cols = [col for col in df.columns if col.endswith("_w")]
price_cols = [col for col in df.columns if col.endswith("_lr")]

# Create output folder
output_dir = "aids_results_final"
os.makedirs(output_dir, exist_ok=True)


def run_residual_tests(model, X, y):
    """Run residual diagnostic tests on the regression model"""
    results = {}

    # Durbin-Watson test for autocorrelation
    results['Durbin-Watson'] = durbin_watson(model.resid)

    # Breusch-Pagan test for heteroskedasticity
    bp_lm, bp_pval, bp_fval, bp_fpval = het_breuschpagan(model.resid, X)
    results['Breusch-Pagan LM'] = bp_lm
    results['Breusch-Pagan p-value'] = bp_pval
    results['Breusch-Pagan sig'] = bp_pval < 0.05

    # ADF test on residuals
    adf_stat, p_val, _, _, crit_vals, _ = adfuller(model.resid)
    results['ADF Statistic'] = adf_stat
    results['ADF p-value'] = p_val
    results['ADF Stationary'] = p_val < 0.05

    # Calculate RMSE
    y_pred = model.predict(X)
    results['RMSE'] = np.sqrt(mean_squared_error(y, y_pred))

    return results


# Loop through each sector to drop (for singularity avoidance)
for drop_sector in share_cols:
    shares_used = [col for col in share_cols if col != drop_sector]

    # Prepare independent variables (log prices + portfolio value)
    exog_vars = price_cols + ['portfolio_value_ln']
    X = sm.add_constant(df[exog_vars])

    # Run OLS for each share equation (excluding dropped sector)
    results = {}
    residual_tests = []

    for share in shares_used:
        y = df[share]
        model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
        results[share] = model

        # Run residual tests
        tests = run_residual_tests(model, X, y)
        residual_tests.append({
            "Dropped": drop_sector,
            "Sector": share,
            **tests
        })

    # Save residual test results
    tests_df = pd.DataFrame(residual_tests)
    tests_file = os.path.join(output_dir, f"residual_tests_dropped_{drop_sector}.csv")
    tests_df.to_csv(tests_file, index=False)


    # Compute elasticities
    def compute_elasticities(results, share_cols, price_cols, df, drop_sector):
        elasticities = pd.DataFrame(index=share_cols, columns=price_cols + ['portfolio_value_ln'])

        for share in results:
            gamma = results[share].params
            for price in price_cols:
                elasticities.loc[share, price] = gamma[price]  # Direct coefficient = elasticity
            elasticities.loc[share, 'portfolio_value_ln'] = gamma['portfolio_value_ln']  # Semi-elasticity

        # Enforce adding-up constraint
        elasticities.loc[drop_sector] = -elasticities.drop(drop_sector).sum(axis=0)

        return elasticities


    elasticities = compute_elasticities(results, share_cols, price_cols, df, drop_sector)

    # Save elasticities
    elasticities_file = os.path.join(output_dir, f"elasticities_dropped_{drop_sector}.csv")
    elasticities.to_csv(elasticities_file)

    # Enhanced model statistics
    model_stats = []
    for share, model in results.items():
        for param in model.params.index:
            model_stats.append({
                "Dropped": drop_sector,
                "Sector": share,
                "Parameter": param,
                "Coefficient": model.params[param],
                "Std Error": model.bse[param],
                "t-value": model.tvalues[param],
                "P-value": model.pvalues[param],
                "R-squared": model.rsquared,
                "Adj R-squared": model.rsquared_adj,
                "F-statistic": model.fvalue,
                "Prob (F-statistic)": model.f_pvalue,
                "RMSE": np.sqrt(mean_squared_error(df[share], model.predict(X)))
            })

    model_stats_df = pd.DataFrame(model_stats)
    stats_file = os.path.join(output_dir, f"model_stats_dropped_{drop_sector}.csv")
    model_stats_df.to_csv(stats_file, index=False)

    print(f"Completed analysis with dropped sector: {drop_sector}")
    print(f"  Avg RMSE: {tests_df['RMSE'].mean():.4f}")
    print(f"  Durbin-Watson range: {tests_df['Durbin-Watson'].min():.2f}-{tests_df['Durbin-Watson'].max():.2f}")
    print(f"  Heteroskedastic cases: {tests_df['Breusch-Pagan sig'].sum()}/{len(tests_df)}")
    print(f"  Stationary residuals: {tests_df['ADF Stationary'].sum()}/{len(tests_df)}\n")

print("FAIDS regression analysis successfully completed with all diagnostics!")
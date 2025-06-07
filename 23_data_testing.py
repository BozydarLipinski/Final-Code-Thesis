import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.regression.linear_model import OLS

# Load your dataset
data = pd.read_csv('AIDS_Data_Final.csv')  # Replace with your filename

# 1. Durbin-Watson Test for Serial Correlation
def run_durbin_watson(weights):
    """Test for autocorrelation in each sector's weights"""
    results = {}
    for col in weights:
        dw_stat = durbin_watson(data[col])
        results[col] = {
            'Durbin-Watson': dw_stat,
            'Interpretation': 'No autocorrelation' if 1.5 < dw_stat < 2.5
                            else 'Positive autocorrelation' if dw_stat < 1.5
                            else 'Negative autocorrelation'
        }
    return pd.DataFrame(results).T

# 2. Augmented Dickey-Fuller Test for Stationarity
def run_adf_tests(weights):
    """Test stationarity of each sector's weights"""
    results = {}
    for col in weights:
        adf_result = adfuller(data[col], autolag='AIC')
        results[col] = {
            'ADF Statistic': adf_result[0],
            'p-value': adf_result[1],
            'Critical Values': adf_result[4],
            'Stationary': adf_result[1] < 0.05
        }
    return pd.DataFrame(results).T



# 3. Variance Inflation Factor for Multicollinearity
def calculate_vif(exog_data):
    """Calculate VIF for explanatory variables"""
    vif_data = pd.DataFrame()
    vif_data["Variable"] = exog_data.columns
    vif_data["VIF"] = [variance_inflation_factor(exog_data.values, i)
                      for i in range(exog_data.shape[1])]
    return vif_data

# 4. Breusch-Pagan Test for Heteroskedasticity
def run_breusch_pagan(weights, exog_vars):
    """Test for heteroskedasticity in each sector's weights"""
    results = {}
    X = sm.add_constant(data[exog_vars])
    for col in weights:
        model = OLS(data[col], X).fit()
        bp_test = het_breuschpagan(model.resid, model.model.exog)
        results[col] = {
            'LM Statistic': bp_test[0],
            'p-value': bp_test[1],
            'Heteroskedasticity': bp_test[1] < 0.05
        }
    return pd.DataFrame(results).T

# Get sector weight columns (assuming they end with '_w')
weight_cols = [col for col in data.columns if col.endswith('_w')]

# Identify return columns (those ending in '_lr')
return_cols = [col for col in data.columns if col.endswith('_lr')]

# Define initial explanatory variables
exog_vars = ['portfolio_value_ln']  # Add other fixed exogenous variables here if needed

# Merge return columns into exog_vars
exog_vars += return_cols

# Run all tests and collect results
all_results = []

# Durbin-Watson Tests
dw_results = run_durbin_watson(weight_cols)
dw_results['Test'] = 'Durbin-Watson'
all_results.append(dw_results)

# ADF Tests for weights
adf_results = run_adf_tests(weight_cols)
adf_results['Test'] = 'ADF (Weights)'
all_results.append(adf_results)

# ADF Tests for explanatory variables
adf_results2 = run_adf_tests(exog_vars)
adf_results2['Test'] = 'ADF (Explanatory Variables)'
all_results.append(adf_results2)

# VIF Tests
vif_results = calculate_vif(data[exog_vars])
vif_results = vif_results.set_index('Variable')
vif_results['Test'] = 'VIF'
all_results.append(vif_results)

# Breusch-Pagan Tests
bp_results = run_breusch_pagan(weight_cols, exog_vars)
bp_results['Test'] = 'Breusch-Pagan'
all_results.append(bp_results)

# Combine all results
final_results = pd.concat(all_results)

# Add a column for the variable name (index becomes a column)
final_results = final_results.reset_index().rename(columns={'index': 'Variable'})

# Reorder columns to have Test and Variable first
cols = ['Test', 'Variable'] + [col for col in final_results.columns if col not in ['Test', 'Variable']]
final_results = final_results[cols]

# Save to CSV
final_results.to_csv('all_diagnostic_tests.csv', index=False)

print("All tests combined and saved to 'all_diagnostic_tests.csv'")

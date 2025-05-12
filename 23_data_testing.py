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

# Run all tests
print("=== Durbin-Watson Tests ===")
dw_results = run_durbin_watson(weight_cols)
print(dw_results)

print("\n=== ADF Stationarity Tests ===")
adf_results = run_adf_tests(weight_cols)
print(adf_results)


print("\n=== ADF Stationarity Tests ===")
adf_results2 = run_adf_tests(data[exog_vars])
print(adf_results2)

print("\n=== VIF Multicollinearity Tests ===")
vif_results = calculate_vif(data[exog_vars])
print(vif_results)



# Create a new version of X excluding Industrials_lr
X_excl_industrials = data[exog_vars].drop(columns=["Industrials_lr"])


print("\n=== VIF Multicollinearity Tests ===")
vif_results2 = calculate_vif(X_excl_industrials)
print(vif_results2)

print("\n=== Breusch-Pagan Heteroskedasticity Tests ===")
bp_results = run_breusch_pagan(weight_cols, exog_vars)
print(bp_results)

# Save results to Excel
# with pd.ExcelWriter('diagnostic_tests_results.xlsx') as writer:
#     dw_results.to_excel(writer, sheet_name='Durbin_Watson')
#     adf_results.to_excel(writer, sheet_name='ADF_Stationarity')
#     vif_results.to_excel(writer, sheet_name='VIF_Multicollinearity')
#     bp_results.to_excel(writer, sheet_name='Breusch_Pagan')
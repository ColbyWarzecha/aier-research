import pandas as pd
import statsmodels.formula.api as smf


data = pd.read_csv("./data/consolidated_data.csv")
data['Open Time'] = pd.to_datetime(data["Open Time"])

results = smf.ols('Open_BTCUSDT ~ Open_USDCHF', data=data).fit()
print(results.summary())
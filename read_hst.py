import mt4_hst

df = mt4_hst.read_hst("./data/USDCHF.hst")

## Simple Diagnostics
# print(df.describe())
# print(df.count())
# print(df.columns)
# print(df.tail(-5))
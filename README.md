# README

Example Run
python -m visualize --currency BTCUSDT

Macnoob setup
```
pip install virtualenv
pip install venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m [script]«
```

## Data Sources

[SPY/SPX Data](https://firstratedata.com/free-intraday-data)
[USD/CHF Data](https://www.fxdd.com/mt/en/market-data/metatrader-1-minute-data)
[BTC/ARS & BTC/USDT](https://data.binance.vision/?prefix=data/spot/daily/klines/)

klines schema for BTC/ARS & BTC/USDT
```
[
  [
    1591258320000,          // Open time
    "9640.7",               // Open
    "9642.4",               // High
    "9640.6",               // Low
    "9642.0",               // Close (or latest price)
    "206",                  // Volume
    1591258379999,          // Close time
    "2.13660389",           // Base asset volume
    48,                     // Number of trades
    "119",                  // Taker buy volume
    "1.23424865",           // Taker buy base asset volume
    "0"                     // Ignore.
  ]
]
```
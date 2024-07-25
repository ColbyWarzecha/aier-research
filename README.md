# Cryptocurrency Market Analysis Tool

This project analyzes the impact of specific political events in Argentina on cryptocurrency markets, particularly focusing on Bitcoin (BTC).

## Table of Contents

- [Cryptocurrency Market Analysis Tool](#cryptocurrency-market-analysis-tool)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Data Sources](#data-sources)


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crypto-market-analysis.git
   cd aier-research
   ```

2. Set up a virtual environment:
   ```bash
   pip install virtualenv
   virtualenv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. For visualizing the data, use:
   ```bash
   python -m src.visualize --event-date 2023-08-14 --time-window 2 --plot-type price
   ```

## Data Sources

- **SPY/SPX Data**: [FirstRateData](https://firstratedata.com/free-intraday-data)
- **USD/CHF Data**: [FXDD](https://www.fxdd.com/mt/en/market-data/metatrader-1-minute-data)
  - Note: On weekends, data are only given for one minute representing the full day (while the FX markets are closed).
- **BTC/ARS & BTC/USDT**: [Binance Vision](https://data.binance.vision/?prefix=data/spot/daily/klines/)

# Cryptocurrency Market Analysis Tool

This project analyzes the impact of specific political events in Argentina on cryptocurrency markets, particularly focusing on Bitcoin (BTC) and its relationship with traditional currencies like the US Dollar (USD) and Swiss Franc (CHF).

## Table of Contents

- [Cryptocurrency Market Analysis Tool](#cryptocurrency-market-analysis-tool)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Data Sources](#data-sources)
  - [Contributing](#contributing)

## Features

- Regression analysis of BTC/USD and USD/CHF pairs around key Argentine political events
- Time window analysis for event impact assessment
- Configurable parameters for currency pairs, event dates, and analysis settings
- Integration with Claude AI for result interpretation

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

1. Configure your analysis parameters in `config.yaml`.

2. Run the main regression script:
   ```bash
   python -m src.regress
   ```

3. For AI interpretation of results, use:
   ```bash
   python -m src.interpret_results
   ```

## Data Sources

- **SPY/SPX Data**: [FirstRateData](https://firstratedata.com/free-intraday-data)
- **USD/CHF Data**: [FXDD](https://www.fxdd.com/mt/en/market-data/metatrader-1-minute-data)
- **BTC/ARS & BTC/USDT**: [Binance Vision](https://data.binance.vision/?prefix=data/spot/daily/klines/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

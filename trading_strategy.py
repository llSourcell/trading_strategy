import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta

def fetch_crypto_data(tickers, period="1mo"):
    data = yf.download(tickers, period=period, interval="1d")['Adj Close']
    return data

def calculate_returns(data):
    return data.pct_change().dropna()

def portfolio_volatility(weights, returns):
    return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))

def portfolio_return(weights, returns):
    return np.sum(returns.mean() * weights) * 252

def optimize_portfolio(returns):
    num_assets = len(returns.columns)
    args = (returns,)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    
    result = minimize(portfolio_volatility, num_assets * [1./num_assets], args=args,
                      method='SLSQP', bounds=bounds, constraints=constraints)
    
    return result.x

def get_real_time_data(tickers):
    real_time_data = {}
    for ticker in tickers:
        crypto = yf.Ticker(ticker)
        info = crypto.info
        real_time_data[ticker] = {
            'price': info.get('regularMarketPrice', 0),
            'volume': info.get('volume24Hr', 0),
            'market_cap': info.get('marketCap', 0),
        }
    return real_time_data

def adjust_weights(optimal_weights, real_time_data, tickers):
    # Simple adjustment based on 24h volume and market cap
    volume_factor = np.array([real_time_data[t]['volume'] for t in tickers])
    market_cap_factor = np.array([real_time_data[t]['market_cap'] for t in tickers])
    
    # Normalize factors
    volume_factor = volume_factor / np.sum(volume_factor)
    market_cap_factor = market_cap_factor / np.sum(market_cap_factor)
    
    # Combine factors with original weights
    adjusted_weights = optimal_weights * 0.6 + volume_factor * 0.2 + market_cap_factor * 0.2
    
    # Normalize to ensure sum is 1
    return adjusted_weights / np.sum(adjusted_weights)

def main():
    # Define cryptocurrency tickers
    tickers = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD']
    
    # Fetch historical data (last month)
    data = fetch_crypto_data(tickers)
    returns = calculate_returns(data)
    
    # Optimize portfolio based on historical data
    optimal_weights = optimize_portfolio(returns)
    
    # Get real-time data
    real_time_data = get_real_time_data(tickers)
    
    # Adjust weights based on real-time data
    final_weights = adjust_weights(optimal_weights, real_time_data, tickers)
    
    # Print results
    print("Optimal Portfolio Allocation (with real-time adjustments):")
    for ticker, weight in zip(tickers, final_weights):
        print(f"{ticker.split('-')[0]}:{weight*100:.2f}")

if __name__ == "__main__":
    main()

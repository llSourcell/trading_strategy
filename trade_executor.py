import subprocess
import json
import openai
from coinbase.wallet.client import Client
from decimal import Decimal
import yfinance as yf

# Coinbase API credentials
API_KEY = ''
API_SECRET = ''

# OpenAI API key (replace with your own)
openai.api_key = ''

# Initialize Coinbase client
client = Client(API_KEY, API_SECRET)

def get_portfolio_allocation():
    result = subprocess.run(['python', 'trading_strategy.py'], capture_output=True, text=True)
    output = result.stdout.strip().split('\n')
    
    allocation = {}
    for line in output[1:]:
        crypto, percentage = line.split(':')
        allocation[crypto] = float(percentage)
    
    return allocation

def get_current_market_data(tickers):
    data = {}
    for ticker in tickers:
        crypto = yf.Ticker(ticker)
        info = crypto.info
        data[ticker] = {
            'price': info.get('regularMarketPrice', 0),
            'volume': info.get('volume24Hr', 0),
            'market_cap': info.get('marketCap', 0),
            'change_24h': info.get('regularMarketChangePercent', 0),
        }
    return data

def analyze_market_conditions(market_data, current_allocation):
    market_summary = "Current market conditions:\n"
    for ticker, data in market_data.items():
        market_summary += f"{ticker}: Price: ${data['price']:.2f}, 24h Change: {data['change_24h']:.2f}%, "
        market_summary += f"Volume: ${data['volume']:,.0f}, Market Cap: ${data['market_cap']:,.0f}\n"
    
    prompt = f"""
    {market_summary}

    Current portfolio allocation:
    {json.dumps(current_allocation, indent=2)}

    Based on these market conditions, is the current portfolio allocation optimal? 
    If not, suggest a new allocation and explain why. Also, if changes are needed, 
    provide a Python code snippet to update the `trading_strategy.py` file.
    """

    response = openai.ChatCompletion.create(
        model="gpt-o1-preview",
        messages=[
            {"role": "system", "content": "You are a cryptocurrency trading expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']

def update_trading_strategy(ai_suggestion):
    if "```python" in ai_suggestion:
        code_start = ai_suggestion.index("```python") + 10
        code_end = ai_suggestion.index("```", code_start)
        new_code = ai_suggestion[code_start:code_end].strip()
        
        with open('trading_strategy.py', 'w') as f:
            f.write(new_code)
        print("Updated trading_strategy.py with AI suggestions.")
    else:
        print("No code changes suggested by AI.")

def main():
    tickers = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD']
    
    # Get current allocation
    current_allocation = get_portfolio_allocation()
    print("Current Allocation:", current_allocation)
    
    # Get current market data
    market_data = get_current_market_data(tickers)
    
    # Analyze market conditions using OpenAI
    ai_analysis = analyze_market_conditions(market_data, current_allocation)
    print("\nAI Analysis:")
    print(ai_analysis)
    
    # Update trading strategy if suggested
    update_trading_strategy(ai_analysis)
    
    # Re-run portfolio allocation after potential updates
    updated_allocation = get_portfolio_allocation()
    print("\nUpdated Allocation:", updated_allocation)
    
    # Get current portfolio
    current_portfolio = get_current_portfolio()
    print("Current Portfolio:", current_portfolio)
    
    # Calculate total portfolio value in USD
    total_value = sum(current_portfolio.values())
    
    # Calculate target amounts for each cryptocurrency
    target_amounts = calculate_target_amounts(updated_allocation, total_value)
    print("Target Amounts:", target_amounts)
    
    # Execute trades to rebalance the portfolio
    execute_trades(current_portfolio, target_amounts)
    
    print("Portfolio rebalancing complete.")

if __name__ == "__main__":
    main()
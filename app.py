from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
import yfinance as yf
from bs4 import BeautifulSoup
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI

# Tool to retrieve stock price from Yahoo Finance

@tool
def get_stock_price(ticker: str) -> str:
    """A tool that fetches the latest stock price for a given ticker symbol from Yahoo Finance.

    Args:
        ticker: A string representing the stock ticker symbol (e.g., "AAPL" for Apple).
    """

    try:
        # Get the current time in EST (Eastern Time Zone)
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))

        # Market open and close times (EST)
        market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)

        stock = yf.Ticker(ticker)
        price = None
        currency = stock.fast_info.get("currency", "USD")

        # Check if the market is open
        if market_open <= current_time <= market_close:
            # Try to get live price
            price = stock.fast_info.get("last_price")
        else:
            # Market is closed, use last closing price
            hist = stock.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]  # Last closing price

        if price is None:
            return "Price unavailable"

        return f"{currency} {price:,.2f}"

    except Exception as e:
        return f"Error fetching price: {e}"


@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()
model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
custom_role_conversions=None,
)


# Import tool from Hub
# image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, get_stock_price, get_current_time_in_timezone], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()
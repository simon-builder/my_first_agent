from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool, LiteLLMModel
import datetime
import requests
import pytz
import yaml
from bs4 import BeautifulSoup
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI

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

model = LiteLLMModel(
    model_id="ollama_chat/deepseek-r1:1.5b",
    api_key="ollama"
)

# model = HfApiModel(
# max_tokens=2096,
# temperature=0.5,
# model_id='http://localhost:11434',
# custom_role_conversions=None,
# )

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, get_current_time_in_timezone],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

GradioUI(agent).launch()
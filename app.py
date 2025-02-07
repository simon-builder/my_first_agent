
from smolagents import GradioUI, CodeAgent, HfApiModel

from scripts.web_search import DuckDuckGoSearchTool
from scripts.visit_webpage import VisitWebpageTool
from scripts.final_answer import FinalAnswerTool


model = HfApiModel(
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',custom_role_conversions=None,)

web_search = DuckDuckGoSearchTool()
visit_webpage = VisitWebpageTool()
final_answer = FinalAnswerTool()


agent = CodeAgent(
    model=model,
    tools=[web_search, visit_webpage, final_answer],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    authorized_imports=['queue', 'statistics', 'pandas', 'random', 'datetime', 'math', 're', 'stat', 'unicodedata', 'collections', 'itertools', 'time'],
    prompts_path='./prompts.yaml'
)

GradioUI(agent).launch()
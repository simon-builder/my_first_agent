
import yaml
from smolagents import GradioUI, CodeAgent, HfApiModel

from tools.web_search import DuckDuckGoSearchTool
from tools.visit_webpage import VisitWebpageTool
from tools.final_answer import FinalAnswerTool


model = HfApiModel(
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
custom_role_conversions=None,
)

web_search = DuckDuckGoSearchTool()
visit_webpage = VisitWebpageTool()
final_answer = FinalAnswerTool()


prompt_templates = yaml.safe_load(
    importlib.resources.files("smolagents.prompts").joinpath("code_agent.yaml").read_text()
)

agent = CodeAgent(
    model=model,
    tools=[web_search, visit_webpage, final_answer],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

GradioUI(agent).launch()
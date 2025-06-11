from camel.agents import ChatAgent
from camel.models import ModelFactory

from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)

from pydantic import BaseModel
from typing import List
import json

class ExplicitNeed(BaseModel):
    categories: List[str]
    attributes: List[str]
    hours: List[str]
    location: List[str]

# model = ModelFactory.create(
#     model_platform=ModelPlatformType.OPENAI,
#     model_type="gpt-4.1-2025-04-14",
#     url="https://api.openai.com/v1/",
# )

model = ModelFactory.create(
    model_platform=ModelPlatformType.MODELSCOPE,
    model_type='Qwen/Qwen2.5-72B-Instruct',
    model_config_dict = {'temperature': 0.2},
)

explicit_need_message = """
You are a friendly assistant helping users find the perfect place or service.

Your task is:

1. Extract from the user's query the explicit needs in four key areas:
   - The type(s) of place or service they are looking for (categories, e.g., restaurant, gym, salon)
   - The specific features or attributes they prefer (attributes, e.g., outdoor seating, wheelchair accessible, family-friendly)
   - The time or hours they plan to visit or use the service (hours, e.g., weekend evenings, weekdays during lunch)
   - The area or location they want to visit (location, e.g., downtown, near Central Park, San Francisco)

2. If any of these categories have no relevant information in the user's query, output an empty list for that category.

3. Do not ask any questions or engage in dialogue; only extract these details from the user’s input.

4. Output ONLY the extracted information in the exact JSON format below, with no extra text or explanation:

{
  "categories": [...],
  "attributes": [...],
  "hours": [...],
  "location": [...]
}
"""

explict_need_agent = ChatAgent(
    system_message=explicit_need_message,
    model=model,
    output_language="en",
)

response = explict_need_agent.step(
    "I'm looking for a cozy brunch place in San Francisco that's good for small groups. ",
    response_format=ExplicitNeed,
)
print(response.msg.content)

dict_obj = json.loads(response.msg.content)
print(dict_obj["categories"])















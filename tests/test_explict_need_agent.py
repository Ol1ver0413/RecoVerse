from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.societies import RolePlaying
from camel.toolkits import HumanToolkit
from camel.messages import BaseMessage
from camel.responses import ChatAgentResponse

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recoverse.utils.conversation_session import ConversationSession

from camel.memories import (
    ChatHistoryBlock,
    LongtermAgentMemory,
    MemoryRecord,
    ScoreBasedContextCreator,
    VectorDBBlock,
)

from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type="gpt-4.1-2025-04-14",
    url="https://api.openai.com/v1/",
)

conversation_message = """
You are a friendly assistant helping users find the perfect place or service.

Your job is to:
1. Ask clarifying questions to understand the user's explicit needs
2. Encourage the user to provide more details (e.g., location, budget, preferences)
3. Once the user says "done", "no more", or "that's all", stop asking questions

Avoid giving recommendations — just help clarify the user's needs in a natural, multi-turn conversation.
"""

explicit_need_message = """
Task Description:
You are an intelligent assistant responsible for identifying **explicit demand keywords** from a multi-turn dialogue between a user and an assistant (AI).

The input will be a **full conversation**, including alternating utterances from both the assistant and the user. Your job is to extract demands that are **explicitly and clearly expressed by the user only** — do **not** consider the assistant's words.

Types of extractable keywords include:
- Categories (e.g., restaurant, hotel)
- Attributes (e.g., quiet, cheap)
- Locations (e.g., Beijing, New York)

Extraction Rules:
1. Extract **only** the keywords that are **explicitly mentioned by the user**. Do **not** infer or assume any information.
2. Do **not** extract any information mentioned by the assistant.
3. Return the keywords **in the same order** as they appear in the user utterances.
4. Output keywords in **English**, separated by commas.
5. **Do not** provide explanations, translations, or any additional content.
6. Extract **no more than 6 keywords** per conversation.

Output Format:
- Input: A multi-turn dialogue between assistant and user
- Output: <keyword 1, keyword 2, ..., keyword 6, ...>

Examples:

- Input:  
  Assistant: Hi! What kind of place are you looking for?  
  User: I'm looking for a quiet coffee shop.  
  Assistant: Any preferred city or neighborhood?  
  User: In New York would be perfect.  
  Assistant: What will you be doing there?  
  User: Mostly reading or working. Ideally with good Wi-Fi.

  Output: coffee shop, quiet, New York, reading, working, good Wi-Fi

- Input:  
  Assistant: Do you have any type of food in mind?  
  User: I'd love a vegan-friendly restaurant.  
  Assistant: Any specific features you're looking for?  
  User: It has to allow pets and have outdoor seating.  
  Assistant: What city are you in?  
  User: I'm in Los Angeles right now.

  Output: vegan-friendly restaurant, pets allowed, outdoor seating, Los Angeles

- Input:  
  Assistant: What do you feel like eating today?  
  User: Maybe something like brunch.  
  Assistant: Any preferences on the environment?  
  User: I prefer cozy places, good for small groups.  
  Assistant: Where are you located?  
  User: I'm spending the weekend in San Francisco.

  Output: brunch, cozy, small groups, San Francisco
"""

conversation_agent = ChatAgent(
    system_message=conversation_message,
    model=model,
    output_language="en",
)

explict_need_agent = ChatAgent(
    system_message=explicit_need_message,
    model=model,
    output_language="en",
)

# query = [
#     "I'm looking for a cozy brunch place in San Francisco that's good for small groups.",
#     "I want a quiet coffee shop in New York where I can read or work for a few hours.",
#     "Can you suggest a vegan-friendly spot in Los Angeles that's also pet-friendly and has outdoor seating"
# ]

session = ConversationSession(conversation_agent)
session.start()
final_input = session.get_full_conversation()
print("\n" + final_input)

response = explict_need_agent.step(final_input)

print("🎯 Extracted Keywords:")
print(response.msg.content)





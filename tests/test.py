from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.societies import RolePlaying
from camel.toolkits import HumanToolkit
from camel.messages import BaseMessage
from camel.responses import ChatAgentResponse

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

agent = ChatAgent(
    system_message="You are a helpful assistant.",
    model=model,
    output_language="en",
)

response = agent.step("hi, I'm Oliver.")
print(response)
print("======================================")

response = agent.step("What's my name?")
print(response)
print("======================================")

print(agent.chat_history)
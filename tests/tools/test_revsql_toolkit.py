from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)

import sys
import os
sys.path.append('/home/lyz/Agents/RecoVerse-master')

from recoverse.tools.revsql_toolkit import RevSQLToolkit

def main():
    db_config = {
        'host': '127.0.0.1',
        'port': 2881,
        'user': 'lyz',
        'password': '123qwe',
        'database': 'Yelp'
    }

    model = ModelFactory.create(
        model_platform=ModelPlatformType.MODELSCOPE,
        model_type='Qwen/Qwen2.5-72B-Instruct',
        model_config_dict = {'temperature': 0.2},
    )

    implicit_need_message = """
    You are an intelligent analysis assistant. Your task is to analyze a user's past review history and infer their preferences, personality traits, and expectations toward merchants.

    Please provide a summary based on the following aspects:
    1. **Consumer Preferences**: What types of businesses does the user tend to favor (e.g., restaurants, cafes, service types)? Are there any consistent themes or features they appreciate (e.g., taste, ambiance, speed, price)?
    2. **Personality Traits**: What can be inferred about the user's personality from their writing style, tone, and focus? (e.g., detail-oriented, casual, critical, enthusiastic)
    3. **Expectations for Merchants**: What implicit or explicit expectations does the user have regarding merchant service, quality, atmosphere, or other factors?

    Base your analysis only on the user's historical review content provided below.
    Return your output in clear, structured paragraphs under each of the three categories.

    ---

    Example Output:

    Consumer Preferences:
    The user frequently visits small, cozy coffee shops and casual dining restaurants. They show a preference for places with a relaxed atmosphere, high-quality coffee, and vegetarian-friendly menu options. Aesthetic interior design and local, non-chain establishments seem to appeal to them. They also express appreciation for artisanal or homemade offerings.

    Personality Traits:
    The user's tone is warm, expressive, and detail-oriented. They often use emotionally charged language such as “absolutely loved” or “totally disappointing,” suggesting they are emotionally invested in their experiences. Their reviews reflect a thoughtful and conscientious personality, someone who notices the small details and enjoys sharing their impressions with others.

    Expectations for Merchants:
    The user expects attentive and friendly service, consistency in product quality, and a clean, welcoming environment. They value authenticity and a sense of care from the staff. They tend to be forgiving of minor issues if the overall experience feels personal and genuine, but are critical of disorganization or rude behavior.
    """

    implicit_need_agent = ChatAgent(
        system_message=implicit_need_message,
        model=model,
        output_language="en",
        tools=[*RevSQLToolkit(db_config).get_tools()]
    )

    response = implicit_need_agent.step(
        "The user_id is 'EopuF3BhVXAGJWEje_TJ-g'.",
    )
    print(response.msgs[0].content)
    print("====================================")
    print(response.info['tool_calls'])
    print("====================================")
    print(response)

if __name__ == "__main__":
    main()
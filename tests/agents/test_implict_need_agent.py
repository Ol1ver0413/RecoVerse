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

def get_user_review_texts(db_config, user_id):
    """
    Retrieve all review texts written by a specific user.

    Parameters:
    db_config (dict): Dictionary containing database connection configuration (host, port, user, password, database).
    user_id (str): The user ID whose reviews are to be retrieved.

    Returns:
    list: A list of strings, where each string is a review written by the user.
    """

    import pymysql

    # Connect to the database
    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
    )

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT r.text AS review_text
            FROM reviews AS r
            WHERE r.user_id = %s;
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            # Extract only the review_text from each result
            return '\n\n'.join(f"review{i+1}: {row['review_text']}" for i, row in enumerate(results))
    finally:
        conn.close()

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
)

db_config = {
    'host': ,
    'port': ,
    'user': ',
    'password': ,
    'database': '
}


user_id = "EopuF3BhVXAGJWEje_TJ-g"

results = get_user_review_texts(db_config, user_id)
print(results)

response = implicit_need_agent.step(results)
print(response.msg.content)

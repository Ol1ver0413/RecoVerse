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

from recoverse.tools.bussql_toolkit import BusinessSQLToolkit

def main():
    db_config = {
        'host': '192.168.1.20',
        'port': 2883,
        'user': 'lyz',
        'password': '123qwe',
        'database': 'Yelp'
    }

    model = ModelFactory.create(
        model_platform=ModelPlatformType.MODELSCOPE,
        model_type='Qwen/Qwen2.5-72B-Instruct',
        model_config_dict = {'temperature': 0.2},
        api_key='84f4bd2b-ebeb-46e0-a3b9-6851e75674b7'
    )

    storage_feature_message = prompt = """
    You are an experienced business analyst. I will provide you with **either** detailed business information **or** multiple user reviews for a specific business.

    Your task is as follows:

    1. **If you receive business information** (such as name, location, categories, attributes, operating hours, etc.), write a concise and informative profile of the business. Highlight its key features, offerings, and unique characteristics that define the type of service or experience it provides. Include relevant amenities and contextual details when available (e.g., parking, Wi-Fi, outdoor seating, ambiance). Avoid making assumptions or evaluations—focus on presenting the business accurately and descriptively.

    2. **If you receive user reviews**, synthesize the feedback into a comprehensive evaluation of the business. Identify common themes, including strengths and weaknesses, across aspects such as service quality, product performance, environment, pricing, and overall experience. Your summary should be objective, analytical, and concise (approximately 200 words), without quoting or repeating the original reviews.

    Ensure your response is well-structured, professional, and useful for someone trying to understand what the business is like or how it is perceived by its customers.

    ---

    ### Example Output 1: (For Business Information Input)

    **Business Profile:**

    Sunflower Café is a cozy and casual vegetarian restaurant located in downtown Phoenix. It specializes in healthy, organic meals and offers a wide selection of vegan, gluten-free, and plant-based options. The café is open seven days a week, with extended morning hours to accommodate breakfast crowds.

    The establishment provides a relaxed and welcoming atmosphere, ideal for both solo diners and small groups. It offers free Wi-Fi, wheelchair accessibility, and outdoor seating. Customers can enjoy complimentary parking in the adjacent lot, and the space is pet-friendly. Popular among locals and tourists alike, Sunflower Café is known for its focus on sustainability, with compostable packaging and eco-friendly practices. Its categories include breakfast & brunch, organic food, and vegan cuisine.

    ---

    ### Example Output 2: (For User Reviews Input)

    **Comprehensive Review Summary:**

    Based on user feedback, Sunflower Café is highly regarded for its fresh, flavorful vegetarian and vegan offerings. Diners frequently praise the quality of the ingredients and the variety of healthy dishes, noting that the menu caters well to diverse dietary preferences. The atmosphere is described as calm and inviting, with many enjoying the outdoor seating and the pet-friendly environment.

    Reviewers consistently highlight the friendly and attentive staff, contributing to a positive overall experience. Free Wi-Fi and convenient parking add to customer satisfaction. While most visitors are pleased with the food, some mention that prices can feel slightly high for the portion sizes, and service may slow down during peak hours. Despite these minor issues, the general sentiment reflects a well-loved café that delivers a thoughtful and health-conscious dining experience.
    """

    storage_feature_agent = ChatAgent(
        system_message=storage_feature_message,
        model=model,
        output_language="en",
        tools=[*BusinessSQLToolkit(db_config).get_tools()]
    )


    response = storage_feature_agent.step(
        "I wanna know the business info of 'gG8opRMkztK0GKiSWbfVlw'.",
    )
    print(response.msgs[0].content)
    print("====================================")
    print(response.info['tool_calls'])
    print("====================================")
    print(response)
    print("====================================")

    response = storage_feature_agent.step(
        "I wanna know the business reviews of 'gG8opRMkztK0GKiSWbfVlw'.",
    )
    print(response.msgs[0].content)
    print("====================================")
    print(response.info['tool_calls'])
    print("====================================")
    print(response)
    

if __name__ == "__main__":
    main()

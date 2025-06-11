from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.messages import BaseMessage
from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)
from camel.societies.workforce import Workforce
from camel.tasks import Task

import textwrap
import sys
import os
sys.path.append('/home/lyz/Agents/RecoVerse-master')

from recoverse.tools.revsql_toolkit import RevSQLToolkit
from recoverse.tools.bussql_toolkit import BusinessSQLToolkit

class UserBusinessMatchingEngine:
    def __init__(self, db_config: dict, model_api_key: str):
        self.db_config = db_config
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.MODELSCOPE,
            model_type='Qwen/Qwen2.5-72B-Instruct',
            model_config_dict={'temperature': 0.2},
            api_key=model_api_key,
        )

        # 把所有prompt都写在这里
        self.storage_feature_message = textwrap.dedent("""
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
        """)

        self.implicit_need_message = textwrap.dedent("""
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
        """)

        self.score_matcher_message = textwrap.dedent("""
        You are an expert in user-business matching. Given a user's implicit needs inferred from their historical reviews, 
        combined with detailed business information and a summarized evaluation of the business based on historical user reviews, 
        your task is to **rigorously and objectively** assess how well the business fits the user's preferences.

        Your analysis should cover multiple dimensions, including but not limited to:

        - Service quality and customer experience: Based on historical consistency, depth of satisfaction, and review sentiments.
        - Business offerings: Relevance, variety, and depth of products or services in relation to the user’s inferred needs.
        - Features and amenities: Whether specific business attributes (e.g., atmosphere, facilities, unique perks) align with user expectations.
        - Location and accessibility: Geographic proximity, ease of access, and relevance to the user’s likely routines or constraints.
        - Price-to-value ratio: How well the pricing aligns with quality and user-perceived value.
        - Reputation and consistency: General public opinion, review stability over time, and credibility.
        - Personalization potential: Ability to cater to the user’s nuanced or emotional preferences, even if not overtly stated.
        - User-type alignment: Fit for users with similar behavior, lifestyle, or demographic characteristics.

        Return the following:

        - A final suitability score on a **strict 1–10 scale**, where 10 indicates an outstanding match and 1 indicates a clear mismatch.
        - A **concise explanation** of the score, clearly stating both strengths (why it matches) and weaknesses (why it may not match), 
        with attention to possible mismatches or uncertainties.

        Do not be lenient — reserve high scores (8–10) only for highly compatible and well-rounded matches.
        """)

        self.rank_message = textwrap.dedent("""
        You are an intelligent recommendation assistant. Based on the final scores of a list of merchants, please select the top three merchants with the highest scores. Sort them from highest to lowest score and present the recommendation to the user. For each recommended merchant, include the Business Name, score, and the corresponding reason for the recommendation.

        Format the output as follows:
        Recommended top three merchants for you are:
        1. Business Name, Score: X.X, Reason: XXXX
        2. Business Name, Score: X.X, Reason: XXXX
        3. Business Name, Score: X.X, Reason: XXXX
        """)

    def create_workforce(self) -> Workforce:
        storage_feature_agent = ChatAgent(
            system_message=self.storage_feature_message,
            model=self.model,
            output_language="en",
            tools=[*BusinessSQLToolkit(self.db_config).get_tools()]
        )

        implicit_need_agent = ChatAgent(
            system_message=self.implicit_need_message,
            model=self.model,
            output_language="en",
            tools=[*RevSQLToolkit(self.db_config).get_tools()]
        )

        score_matcher_agent = ChatAgent(
            system_message=self.score_matcher_message,
            model=self.model,
            output_language="en"
        )

        rank_agent = ChatAgent(
            system_message=self.rank_message,
            model=self.model,
            output_language="en"
        )

        workforce = Workforce(
            "User Intent-Service Matching Intelligence Engine",
            coordinator_agent_kwargs={"model": self.model},
            task_agent_kwargs={"model": self.model},
            new_worker_agent_kwargs={"model": self.model},
        )

        workforce.add_single_agent_worker(
            "User Preference Analyst: Responsible for analyzing users' past reviews to identify their implicit needs, interests, and service expectations, providing a foundation for personalized matching.",
            worker=implicit_need_agent,
        ).add_single_agent_worker(
            "Business Insight Synthesizer: Responsible for analyzing either detailed business profiles or user reviews to generate concise, objective summaries highlighting key features, strengths, and weaknesses for evaluation and recommendation.",
            worker=storage_feature_agent,
        ).add_single_agent_worker(
            "User-Business Fit Evaluator: Responsible for assessing how well a business aligns with a user's preferences based on their implicit needs, business features, and historical user reviews.",
            worker=score_matcher_agent,
        ).add_single_agent_worker(
            "Top Merchant Recommender: Responsible for selecting the top three merchants with the highest scores based on user preferences and business characteristics.",
            worker=rank_agent,
        )

        return workforce
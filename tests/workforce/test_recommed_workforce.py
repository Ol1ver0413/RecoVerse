from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)
from camel.societies.workforce import Workforce
from camel.tasks import Task

from camel.messages import BaseMessage
from camel.tasks import Task

import textwrap
import sys
import os
sys.path.append('/home/lyz/Agents/RecoVerse-master')

from recoverse.workforce.recommend_workforce import UserBusinessMatchingEngine

def main():
        
    db_config = {
        'host': '127.0.0.1',
        'port': 2881,
        'user': 'lyz',
        'password': '123qwe',
        'database': 'Yelp'
    }

    proj_content= textwrap.dedent(
        """\
        Project Name: User Implicit Needs Insight and Scoring System Based on Reviews and Merchant Information
        How Your Project Solves a Real Problem:  
        This system analyzes users' historical reviews along with merchant information to identify users' implicit needs, interests, and service expectations, addressing the limitations of traditional explicit demand extraction. It helps merchants gain precise insights into user sentiments, improving service quality and customer satisfaction. By aggregating historical reviews, the system also summarizes users' overall evaluation trends, assisting merchants in optimizing products and services.
        Explanation of Your Technology and Which Parts Are Effective:  
        Our system mainly consists of the following core modules:  
        1. Implicit Needs Identification: Using natural language processing techniques to deeply extract latent needs and preferences from user reviews, beyond explicit textual information.  
        2. Merchant Information Integration: Aggregating merchant basic data and service characteristics to provide contextual support for demand matching.  
        3. Review Content Summarization: Utilizing text summarization techniques to aggregate and distill users’ historical reviews into concise evaluation summaries.  
        4. Scoring Mechanism Design: Automatically generating comprehensive scores based on the satisfaction of implicit needs and sentiment analysis of reviews, reflecting overall user satisfaction.  
        Currently, the implicit needs identification and merchant information integration modules have been implemented, while the review summarization and scoring mechanism are under improvement.
        """
    )

    workforce = UserBusinessMatchingEngine(db_config, api_key).create_workforce()

    task = Task(
        content = "For user ID 'EopuF3BhVXAGJWEje_TJ-g' and business ID 'gG8opRMkztK0GKiSWbfVlw', perform a comprehensive compatibility scoring between the user and the business.",
        additional_info = proj_content,
        id = "0"
    )

    task = workforce.process_task(task)
    print(task.result)

if __name__ == "__main__":
    main()

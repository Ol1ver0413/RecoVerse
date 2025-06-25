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

from string import Template
import textwrap
import pymysql
import sys
import os
sys.path.append('/home/lyz/Agents/RecoVerse-master')

from recoverse.workforce.recommend_workforce import UserBusinessMatchingEngine

from camel.embeddings import SentenceTransformerEncoder
from camel.storages.vectordb_storages import (
    OceanBaseStorage,
    VectorDBQuery,
    VectorRecord,
)
from camel.retrievers import VectorRetriever

def get_userid_by_username(db_config, username):
    # 连接到 MySQL 数据库
    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
    )
    
    try:
        with conn.cursor() as cursor:
            # 查询用户名对应的 userid
            query = "SELECT user_id FROM users WHERE name = %s"
            cursor.execute(query, (username,))
            
            # 获取查询结果
            result = cursor.fetchone()
            
            # 如果找到用户，返回 userid
            if result:
                return result[0]
            else:
                return None
    finally:
        # 关闭数据库连接
        conn.close()

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

    examples = [
    ('Looking for a sushi restaurant downtown.', 'Jimmy'),
    ('I need a gym with personal trainers nearby.', 'Monera'),
    ('Can you find a pet store that sells organic food?', 'Elizabeth'),
    ('I want to get a haircut and maybe some styling done.', 'Jacque'),
    ('Need someone to fix my car’s engine and check the tires.', 'David'),
    ('Planning to relax with a massage this weekend.', 'Michelle'),
    ('Searching for a coffee shop or bakery open late.', 'Brian'),
    ('I have to visit the dentist and also get a facial.', 'Keny'),
    ('Looking for something fun to do with kids this Saturday.', 'Leonel'),
    ('I’m craving some food before catching a movie.', 'Russell'),
    ('Just wandering around, no specific plans.', 'Talia'),
    ('Not sure what I want, just exploring options.', 'Susan'),
    ('Need a daycare center that accepts infants.', 'Chantelle'),
    ('Looking for a 24-hour pharmacy nearby.', 'Andrew'),
    ('Want to find a place to learn painting classes.', 'Harry'),
    ]
    
    explict_need_message ="""
    You are a friendly assistant helping users find the perfect place or service.

    Your task is:

    1. From the user's query, extract the **explicit or reasonably inferable category** of place or service they are looking for.

    - If the category is clearly mentioned (e.g., "Italian restaurant", "fitness gym"), extract it **exactly and specifically**, including modifiers like cuisine type, service type, or specialty. Avoid overly broad or generic categories 
    (e.g., do NOT extract just "restaurant" if "Italian restaurant" is mentioned).

    - If it’s not explicitly stated but can be reasonably inferred from context (e.g., "I want to get my nails done" → "nail salon"), extract the most precise, specific category possible.

    2. Output a list of detected or inferred categories. If there is truly no clue, output an empty list.

    3. Do **not** extract features, time, or location. Focus **only** on extracting or inferring the most specific category of place or service.

    4. Do not ask questions or engage in dialogue. Only return the extracted list.

    Examples:

    Input: "I'm looking for a nice Italian restaurant or maybe a cozy café."  
    Output: Italian restaurant, coffee shop

    Input: "Need someone to fix my brakes and rotate my tires."  
    Output: car repair shop

    Input: "I just want to get a massage and relax this afternoon."  
    Output: spa

    Input: "Thinking of going somewhere fun with the kids this weekend."  
    Output: family entertainment center

    Input: "I need to buy dog food and some toys."  
    Output: pet supply store
    """

    explict_need_agent = ChatAgent(
        system_message=explict_need_message,
        model=model,
        output_language="en"
    )
    
    response = explict_need_agent.step(examples[0][0]).msg.content
    print(response)

    user_id = get_userid_by_username(db_config, examples[0][1])
    print(user_id)
    

    embed_model = SentenceTransformerEncoder(model_name="/home/lyz/Rag/models/bge-m3")
    ob_storage = OceanBaseStorage(
        vector_dim=embed_model.get_output_dim(),
        table_name="business_vector",
        uri="192.168.1.20:2883",
        user="lyz",
        password="123qwe",
        db_name="Yelp",
        distance="cosine",
    )

    vr = VectorRetriever(
        embedding_model=embed_model,
        storage=ob_storage,
    )

    results = vr.query(query=response, similarity_threshold=0.6, top_k=5)
    print([res['metadata']['business_name'] for res in results if res['metadata']['business_id'] != 0])

    business_id = [res['metadata']['business_id'] for res in results if res['metadata']['business_id'] != 0]
    print(business_id)

    proj_content= textwrap.dedent(
        """\
        Project Name: User Implicit Needs Insight and Scoring System Based on Reviews and Merchant Information

        How Your Project Solves a Real Problem:  
        This system combines information from multiple merchants with users' historical review ratings to generate separate comprehensive scores for both merchants and users. By deeply extracting implicit needs and sentiment from user reviews, it helps merchants accurately understand users' latent demands, improving service quality and customer satisfaction. At the same time, the system summarizes users' overall evaluation trends from their historical reviews, assisting merchants in optimizing products and services, addressing the limitations of traditional explicit demand extraction. Ultimately, the system selects the top three highest scoring merchants to recommend or highlight.

        Explanation of Your Technology and Which Parts Are Effective:  
        The system consists of the following core modules:  
        1. Implicit Needs Identification: Using natural language processing techniques to deeply extract latent needs and preferences from user reviews, going beyond explicit textual information.  
        2. Merchant Information Integration: Aggregating basic information and service features of multiple merchants to provide contextual support for demand matching.  
        3. Review Content Summarization: Summarizing users’ historical reviews through text summarization techniques to produce concise evaluation overviews.  
        4. Scoring Mechanism Design: Generating comprehensive scores separately for merchant information and user reviews, based on implicit needs satisfaction and sentiment analysis, reflecting overall user satisfaction and merchant performance.  
        5. Top Selection: Selecting the top three merchants with the highest scores for recommendation or further focus.  
        Currently, the implicit needs identification and merchant information integration modules have been implemented, while the review summarization, scoring mechanism, and top selection are under ongoing improvement.
        """
    )

    workforce = UserBusinessMatchingEngine(db_config, api_key).create_workforce()
    input = Template("For user ID $user_id and business ID $business_id, perform a comprehensive compatibility scoring between the user and the business, and also select the top three businesses with the highest compatibility scores for the user.")
    content = input.substitute(user_id=user_id, business_id=business_id)
    print(content)

    task = Task(
        content = content,
        id = "0"
    )

    task = workforce.process_task(task)
    print(task.result)

if __name__ == "__main__":
    main()


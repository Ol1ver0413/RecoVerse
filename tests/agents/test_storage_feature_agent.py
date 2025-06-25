import pymysql
from camel.agents import ChatAgent
from camel.models import ModelFactory

from camel.types import (
    ModelPlatformType,
    ModelType,
    OpenAIBackendRole,
    RoleType,
    TaskType,
)

import random

model = ModelFactory.create(
    model_platform=ModelPlatformType.MODELSCOPE,
    model_type='Qwen/Qwen2.5-72B-Instruct',
    model_config_dict = {'temperature': 0.2},
)

storage_feature_message = """
You are an experienced review analyst. I will provide you with multiple user reviews for a specific business.

Your task is to:
1. Analyze all the reviews and identify common strengths and weaknesses mentioned by users;
2. Provide a concise, well-structured, and objective summary of the business, covering aspects such as service quality, product performance, and overall experience;
3. Do not quote or repeat the original reviews—synthesize the information instead;
4. Keep the summary around 200 words.

Please generate a comprehensive evaluation of the business based on the reviews provided.
"""

def get_business_info(db_config, business_ids):
    """
    Retrieve business information for a list of business IDs.

    Parameters:
    db_config (dict): Dictionary containing database connection configuration (host, port, user, password, database).
    business_ids (list): List of business IDs to retrieve information for.

    Returns:
    list: A list of dictionaries, where each dictionary contains business details.
    """
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
            # Use %s placeholders for each business ID
            placeholders = ','.join(['%s'] * len(business_ids))
            query = f"""
            SELECT 
                business_id,
                name,
                city,
                address,
                attributes,
                categories,
                hours
            FROM business
            WHERE business_id IN ({placeholders});
            """
            cursor.execute(query, tuple(business_ids))
            results = cursor.fetchall()
            # Return the list of business dictionaries directly
            return results
    finally:
        conn.close()

def get_business_reviews(db_config, business_ids):
    """
    Retrieve all review texts for a list of business IDs.

    Parameters:
    db_config (dict): Dictionary containing database connection configuration (host, port, user, password, database).
    business_ids (list): List of business IDs whose reviews are to be retrieved.

    Returns:
    dict: A dictionary where keys are business IDs and values are lists of review text strings.
    """
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
            # Use %s placeholders for each business ID
            placeholders = ','.join(['%s'] * len(business_ids))
            query = f"""
            SELECT 
                business_id,
                text AS review_text
            FROM reviews
            WHERE business_id IN ({placeholders})
            ORDER BY business_id;
            """
            cursor.execute(query, tuple(business_ids))
            results = cursor.fetchall()
            
            # Initialize dictionary to store reviews by business ID
            reviews_by_business = {bid: [] for bid in business_ids}
            
            # Group reviews by business ID
            for row in results:
                business_id = row['business_id']
                reviews_by_business[business_id].append(row['review_text'])

            # Format each business's reviews into a single string
            for business_id in reviews_by_business:
                reviews = reviews_by_business[business_id]
                sampled_reviews = random.sample(reviews, min(10, len(reviews)))  # randon 10(max)
                
                formatted_reviews = []
                for i, review in enumerate(sampled_reviews, start=1):
                    formatted_reviews.append(f"Review {i}: \n{review}")
                
                reviews_by_business[business_id] = '\n\n'.join(formatted_reviews)
            
            return reviews_by_business
        
    finally:
        conn.close()

business_ids = ['gG8opRMkztK0GKiSWbfVlw', 'K1h9s1n2679DxUM2cuMZXA']

db_config = {
    'host': '127.0.0.1',
    'port': 2881,
    'user': 'lyz',
    'password': '123qwe',
    'database': 'Yelp'
}

results = get_business_reviews(db_config, business_ids)

storage_feature_agent = ChatAgent(
    system_message=storage_feature_message,
    model=model,
    output_language="en",
)

for key, value in results.items():
    input = value
    print(f"Business ID: {key}")
    print(f"{value}")
    print("============================================")
    


result = storage_feature_agent.step(input)
print(result.msg.content)

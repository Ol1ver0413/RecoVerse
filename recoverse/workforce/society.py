from string import Template
import textwrap
import pymysql

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import (
    ModelPlatformType,
)
from camel.tasks import Task
from recoverse.workforce.recommend_workforce import UserBusinessMatchingEngine
from camel.retrievers import VectorRetriever
from camel.storages.vectordb_storages import OceanBaseStorage
from camel.embeddings import SentenceTransformerEncoder


class UserBusinessRecommender:
    """
    用户商户匹配推荐系统类：
    给定用户名和查询文本，识别其显性需求，检索匹配商家，调用智能体进行打分推荐。
    """

    def __init__(self, db_config: dict, api_key: str, embed_model: SentenceTransformerEncoder):
        self.db_config = db_config
        self.api_key = api_key
        self.embed_model = embed_model

        # 初始化主模型
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.MODELSCOPE,
            model_type='Qwen/Qwen2.5-72B-Instruct',
            model_config_dict={'temperature': 0.2},
            api_key=api_key
        )

        # 显性需求提示词：精确识别服务类别
        self.explicit_need_prompt = textwrap.dedent("""
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
        """)

        # 显性需求识别 Agent
        self.explicit_need_agent = ChatAgent(
            system_message=self.explicit_need_prompt,
            model=self.model,
            output_language="en"
        )

        # 向量数据库初始化
        self.vector_storage = OceanBaseStorage(
            vector_dim=self.embed_model.get_output_dim(),
            table_name="business_vector",
            uri=f"{db_config['host']}:{db_config['port']}",
            user=db_config["user"],
            password=db_config["password"],
            db_name=db_config["database"],
            distance="cosine"
        )
        self.retriever = VectorRetriever(
            embedding_model=self.embed_model,
            storage=self.vector_storage
        )

        # 项目内容：用于展示或文档输出
        self.proj_content = textwrap.dedent("""\
        Project Name: User Implicit Needs Insight and Scoring System Based on Reviews and Merchant Information

        How Your Project Solves a Real Problem:  
        This system combines information from multiple merchants with users' historical review ratings to generate separate comprehensive scores for both merchants and users. By deeply extracting implicit needs and sentiment from user reviews, it helps merchants accurately understand users' latent demands, improving service quality and customer satisfaction. At the same time, the system summarizes users' overall evaluation trends from their historical reviews, assisting merchants in optimizing products and services, addressing the limitations of traditional explicit demand extraction. Ultimately, the system selects the top three highest scoring merchants to recommend or highlight.

        Explanation of Your Technology and Which Parts Are Effective:  
        The system consists of the following core modules:  
        1. Implicit Needs Identification: Using natural language processing techniques to deeply extract latent needs and preferences from user reviews, going beyond explicit textual information.  
        2. Merchant Information Integration: Aggregating basic information and service features of multiple merchants to provide contextual support for demand matching.  
        3. Review Content Summarization: Summarizing users' historical reviews through text summarization techniques to produce concise evaluation overviews.  
        4. Scoring Mechanism Design: Generating comprehensive scores separately for merchant information and user reviews, based on implicit needs satisfaction and sentiment analysis, reflecting overall user satisfaction and merchant performance.  
        5. Top Selection: Selecting the top three merchants with the highest scores for recommendation or further focus.  
        Currently, the implicit needs identification and merchant information integration modules have been implemented, while the review summarization, scoring mechanism, and top selection are under ongoing improvement.
        """)

    def get_user_id(self, username: str) -> int:
        """
        根据用户名从数据库中查询 user_id。
        """
        conn = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database']
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE name = %s", (username,))
                result = cursor.fetchone()
                return result[0] if result else None
        finally:
            conn.close()

    def extract_explicit_category(self, query: str) -> str:
        """
        使用语言模型从查询中识别精确服务类别。
        """
        return self.explicit_need_agent.step(query).msg.content

    def retrieve_business_ids(self, category_str: str) -> list:
        """
        使用向量检索器获取与服务类别最相似的商家ID。
        """
        results = self.retriever.query(query=category_str, similarity_threshold=0.6, top_k=5)
        return [
            res['metadata']['business_id']
            for res in results if res['metadata']['business_id'] != 0
        ]

    def recommend(self, username: str, query: str) -> str:
        """
        核心流程函数：执行需求提取、商家检索、评分推荐并返回结果。
        """
        # Step 1: 用户身份识别
        user_id = self.get_user_id(username)
        if user_id is None:
            return f"用户 {username} 不存在。"

        # Step 2: 显性需求识别
        category_str = self.extract_explicit_category(query)
        print(f"[显性需求识别] → {category_str}")

        # Step 3: 商家向量检索
        business_ids = self.retrieve_business_ids(category_str)
        print(f"[检索到商家ID] → {business_ids}")

        if not business_ids:
            return "未能检索到匹配商家，请尝试修改查询。"

        # Step 4: 构造推荐任务
        prompt = Template(
            "For user ID $user_id and business ID $business_id, perform a comprehensive compatibility scoring between the user and the business, and also select the top three businesses with the highest compatibility scores for the user."
        )
        task_content = prompt.substitute(user_id=user_id, business_id=business_ids)

        # Step 5: 调用智能体进行评分与推荐
        task = Task(content=task_content, id="0")
        workforce = UserBusinessMatchingEngine(self.db_config, self.api_key).create_workforce()
        result = workforce.process_task(task).result

        return result

if __name__ == "__main__":
    db_config = {
        'host': '192.168.1.20',
        'port': 2883,
        'user': 'lyz',
        'password': '123qwe',
        'database': 'Yelp'
    }

    embed_model = SentenceTransformerEncoder(model_name="/home/lyz/Rag/models/bge-m3")

    recommender = UserBusinessRecommender(
        db_config=db_config,
        api_key='84f4bd2b-ebeb-46e0-a3b9-6851e75674b7',
        embed_model=embed_model
    )

    result = recommender.recommend(username="Jimmy", query="Looking for a sushi restaurant downtown.")
    print("[推荐结果]：")
    print(result)

    print("\n[项目介绍内容]：")
    print(recommender.proj_content)

from camel.toolkits.base import BaseToolkit
from camel.toolkits.function_tool import FunctionTool

from typing import Dict, List, Any
import pymysql
import random

class BusinessSQLToolkit(BaseToolkit):
    def __init__(self, db_config: Dict[str, Any]):
        """
        初始化数据库连接配置。
        """
        self.db_config = db_config

    def get_business_info(self, business_ids: List[str]) -> List[Dict[str, Any]]:
        """
        获取一组 business_id 的商户基本信息。

        参数:
        - business_ids: 商户 ID 列表

        返回:
        - 包含每个商户信息的字典列表，包括名称、地址、类别、属性、营业时间等字段
        """
        conn = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
        )

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
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
                return cursor.fetchall()
        finally:
            conn.close()

    def get_business_reviews(self, business_ids: List[str]) -> Dict[str, str]:
        """
        获取一组 business_id 的评论文本（每个商户最多 10 条）。

        参数:
        - business_ids: 商户 ID 列表

        返回:
        - 一个字典，键为商户 ID，值为拼接后的最多 10 条格式化评论文本
        """
        conn = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
        )

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
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

                reviews_by_business = {bid: [] for bid in business_ids}
                for row in results:
                    reviews_by_business[row['business_id']].append(row['review_text'])

                for business_id in reviews_by_business:
                    reviews = reviews_by_business[business_id]
                    sampled_reviews = random.sample(reviews, min(10, len(reviews)))
                    formatted_reviews = [f"Review {i + 1}: \n{review}" for i, review in enumerate(sampled_reviews)]
                    reviews_by_business[business_id] = '\n\n'.join(formatted_reviews)

                return reviews_by_business
        finally:
            conn.close()

    def get_tools(self) -> List[FunctionTool]:
        """
        返回 FunctionTool 对象列表，用于注册该 toolkit 中的工具方法。
        """
        return [
            FunctionTool(self.get_business_info),
            FunctionTool(self.get_business_reviews)
        ]
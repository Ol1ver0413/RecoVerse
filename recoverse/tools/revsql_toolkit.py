from camel.toolkits.base import BaseToolkit
from camel.toolkits.function_tool import FunctionTool

from typing import Dict, List
import pymysql

class RevSQLToolkit(BaseToolkit):
    def __init__(self, db_config: Dict):
        """
        初始化数据库连接配置。

        参数:
        - db_config: 包含数据库连接信息的字典（host, port, user, password, database）
        """
        self.db_config = db_config

    def get_user_review_texts(self, user_id: str) -> str:
        """
        从数据库中检索指定用户撰写的所有评论文本。

        参数:
        - user_id: 需要检索评论的用户 ID

        返回:
        - 一个字符串，包含该用户所有评论，每条评论前缀为 review{i}:
        """
        # 连接数据库
        conn = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
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
                return '\n\n'.join(f"review{i+1}: {row['review_text']}" for i, row in enumerate(results))
        finally:
            conn.close()

    def get_tools(self) -> List[FunctionTool]:
        """
        返回 FunctionTool 对象列表，用于注册该 toolkit 中的工具方法。
        """
        return [
            FunctionTool(self.get_user_review_texts)
        ]
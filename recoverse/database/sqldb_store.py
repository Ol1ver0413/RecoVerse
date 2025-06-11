from tqdm import tqdm
import pymysql
import json

from tqdm import tqdm
import pymysql
import json

class YelpDataInserter():
    """
    A class to handle inserting Yelp dataset data (users, businesses, reviews)
    into a MySQL database.
    """

    def __init__(self, db_config):
        """
        Initialize the inserter with database configuration.

        :param db_config: dict containing 'host', 'port', 'user', 'password', 'database'
        """
        self.db_config = db_config

    def _connect(self):
        """
        Create and return a new database connection and cursor.

        :return: (conn, cursor) tuple
        """
        conn = pymysql.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
        )
        cursor = conn.cursor()
        return conn, cursor

    def insert_user_data(self, json_file_path):
        """
        Insert user data from a JSON (NDJSON) file into the 'users' table.

        :param json_file_path: Path to the NDJSON file containing user records
        """
        # Read JSON lines
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                lines = [line for line in f.read().splitlines() if line.strip()]
                users_data = [json.loads(line) for line in lines]
        except Exception as e:
            print(f"Failed to read user JSON file: {e}")
            return

        conn, cursor = None, None
        try:
            conn, cursor = self._connect()
            print("Connected to database for user insertion.")

            # Ensure table exists
            create_query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                review_count INT,
                friends_count INT,
                fans_count INT
            );
            """
            cursor.execute(create_query)

            # Insert SQL
            insert_sql = """
            INSERT INTO users (user_id, name, review_count, friends_count, fans_count)
            VALUES (%s, %s, %s, %s, %s);
            """

            for user in tqdm(users_data, desc="Inserting users", unit="user"):
                cursor.execute(
                    insert_sql,
                    (
                        user['user_id'],
                        user.get('name'),
                        user.get('review_count'),
                        len(user.get('friends', '').split(', ')),
                        user.get('fans')
                    )
                )
            conn.commit()
            print("All user records inserted successfully.")

        except Exception as e:
            print(f"Error inserting user data: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def insert_business_data(self, json_file_path):
        """
        Insert business data from a JSON (NDJSON) file into the 'business' table.

        :param json_file_path: Path to the NDJSON file containing business records
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                lines = [line for line in f.read().splitlines() if line.strip()]
                businesses_data = [json.loads(line) for line in lines]
        except Exception as e:
            print(f"Failed to read business JSON file: {e}")
            return

        conn, cursor = None, None
        try:
            conn, cursor = self._connect()
            print("Connected to database for business insertion.")

            create_query = """
            CREATE TABLE IF NOT EXISTS business (
                business_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                address VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                postal_code VARCHAR(20),
                stars FLOAT,
                review_count INT,
                is_open INT,
                attributes TEXT,
                categories TEXT,
                hours JSON
            );
            """
            cursor.execute(create_query)

            insert_sql = """
            INSERT INTO business 
            (business_id, name, address, city, state, postal_code,
             stars, review_count, is_open, attributes, categories, hours)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            for biz in tqdm(businesses_data, desc="Inserting businesses", unit="business"):
                cursor.execute(
                    insert_sql,
                    (
                        biz['business_id'],
                        biz.get('name'),
                        biz.get('address'),
                        biz.get('city'),
                        biz.get('state'),
                        biz.get('postal_code'),
                        biz.get('stars'),
                        biz.get('review_count'),
                        biz.get('is_open'),
                        json.dumps(biz.get('attributes', {})),
                        biz.get('categories'),
                        json.dumps(biz.get('hours', {}))
                    )
                )
            conn.commit()
            print("All business records inserted successfully.")

        except Exception as e:
            print(f"Error inserting business data: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def insert_review_data(self, json_file_path):
        """
        Insert review data from a JSON (NDJSON) file into the 'reviews' table.

        :param json_file_path: Path to the NDJSON file containing review records
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                lines = [line for line in f.read().splitlines() if line.strip()]
                reviews_data = [json.loads(line) for line in lines]
        except Exception as e:
            print(f"Failed to read review JSON file: {e}")
            return

        conn, cursor = None, None
        try:
            conn, cursor = self._connect()
            print("Connected to database for review insertion.")

            create_query = """
            CREATE TABLE IF NOT EXISTS reviews (
                review_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255),
                business_id VARCHAR(255),
                stars FLOAT,
                useful INT,
                funny INT,
                cool INT,
                text TEXT,
                date DATETIME
            );
            """
            cursor.execute(create_query)

            insert_sql = """
            INSERT INTO reviews 
            (review_id, user_id, business_id, stars, useful, funny, cool, text, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            for rev in tqdm(reviews_data, desc="Inserting reviews", unit="review"):
                cursor.execute(
                    insert_sql,
                    (
                        rev['review_id'],
                        rev.get('user_id'),
                        rev.get('business_id'),
                        rev.get('stars'),
                        rev.get('useful'),
                        rev.get('funny'),
                        rev.get('cool'),
                        rev.get('text'),
                        rev.get('date')
                    )
                )
            conn.commit()
            print("All review records inserted successfully.")

        except Exception as e:
            print(f"Error inserting review data: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

def main():
    # 1. 定义数据库连接配置
    db_config = {
        'host': '192.168.1.20',
        'port': 2881,
        'user': 'lyz',
        'password': '123qwe',
        'database': 'Yelp'
    }

    # 2. 创建插入器实例
    Inserter = YelpDataInserter(db_config)

    # 3. 分别调用不同方法插入数据
    # 注意：下面路径请替换成你本地的实际文件路径
    Inserter.insert_user_data(
        '/home/lyz/Agents/RecommendAgent/datasets/Yelp/yelp_academic_dataset_user.json'
    )
    inserter.insert_business_data(
        '/home/lyz/Agents/RecommendAgent/datasets/Yelp/yelp_academic_dataset_business.json'
    )
    inserter.insert_review_data(
        '/home/lyz/Agents/RecommendAgent/datasets/Yelp/yelp_academic_dataset_review.json'
    )

    print("所有 Yelp 数据已导入完成！")


if __name__ == "__main__":
    main()

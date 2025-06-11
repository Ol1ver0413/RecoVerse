from camel.embeddings import SentenceTransformerEncoder
from camel.retrievers import VectorRetriever
from camel.storages import OceanBaseStorage
from camel.storages import VectorDBQuery, VectorRecord
from tqdm import tqdm
import json

def convert_business_json_to_vectors(json_file_path: str,
                                     embed_model: SentenceTransformerEncoder,
                                     vector_storage: OceanBaseStorage):
    """
    读取 business JSON 文件中的每条记录，将 categories 字段转换为向量，
    并将 business_id 作为元数据存储到向量存储中，过程带有 tqdm 进度条。
    """
    try:
        # 先读取所有数据
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = f.read()
            businesses_data = [json.loads(line) for line in data.splitlines() if line.strip()]

        # 逐条处理，并显示进度
        for i, item in enumerate(tqdm(businesses_data, desc="Embedding & Storing", unit="item")):
            # 安全获取 categories 字段
            categories = item.get("categories")
            if not categories:
                print(f"第 {i} 条数据缺失或为空的 categories，跳过")
                continue

            # 获取 categories 字段并转换为向量
            cate_vector = embed_model.embed_list([categories])[0]

            # 构造 VectorRecord
            vr = VectorRecord(
                vector=cate_vector,
                payload={
                    "metadata": {
                        "business_id": item["business_id"],   
                        "business_name": item["name"],
                        "business_categories": categories,
                        "business_is_open": item["is_open"],
                    },
                }
            )

            # 添加到存储（可改为批量 add）
            vector_storage.add([vr])

        print(f"全部处理完成，共处理有效记录 {len(businesses_data)} 条。")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

def main():
    # 示例：初始化 embedding 模型和向量存储
    embed_model = SentenceTransformerEncoder(model_name="/home/lyz/Rag/models/bge-m3")
    vector_storage = OceanBaseStorage(
        vector_dim=embed_model.get_output_dim(),
        table_name="business_vector",
        uri="192.168.1.20:2883",
        user="lyz",
        password="123qwe",
        db_name="Yelp",
        distance="cosine",
    )

    # 调用处理函数
    convert_business_json_to_vectors("/home/lyz/Agents/RecommendAgent/datasets/Yelp/yelp_academic_dataset_business.json", embed_model, vector_storage)

if __name__ == "__main__":
    main()
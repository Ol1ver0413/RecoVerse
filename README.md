# RecoVerse 🌌 — A Multi-Agent Recommendation System

**RecoVerse** is an intelligent, modular, and extensible multi-agent recommendation system. It leverages the power of collaborative agents to deliver personalized, explainable, and adaptive recommendations across domains.

## 🚀 Overview

RecoVerse transforms traditional recommendation pipelines by introducing **Multi-Agent Collaboration**, where each agent is responsible for a specific cognitive task — from understanding user intent to reasoning over historical data and generating tailored suggestions.

### ✨ Key Features

- 🤖 **Multi-Agent Architecture**: Decentralized agents handle user modeling, content analysis, filtering, ranking, and explanation tasks.
- 🧠 **Intent-Aware**: Agents jointly infer both explicit and *implicit* user needs based on behavior, preferences, and feedback.
- 🔄 **Pluggable Workflows**: Easily extend or replace agents for domain-specific customization.
- 📊 **Hybrid Recommendations**: Supports collaborative filtering, content-based methods, and rule-augmented heuristics.
- 🧩 **Explainability**: Provide reasoning traces from agents for every recommendation.

---

### 🧭 System Workflow

![RecoVerse Workflow](https://github.com/Ol1ver0413/RecoVerse/blob/master/pictures/flow_chat.jpg)

---

## 📦 Installation

1. Clone this repository:

```bash
git clone https://github.com/Ol1ver0413/RecoVerse.git
cd RecoVerse
```
2. Install dependencies:
pip install -r requirements.txt

## ⚙️ Configuration
Before running the system, ensure your database and embedding model are correctly configured. Update main.py or your own script with the following:

```python
db_config = {
    'host': '127.0.0.1',
    'port': 2881,
    'user': 'lyz',
    'password': '123qwe',
    'database': 'Yelp'
}

from recosystem.embedding import SentenceTransformerEncoder
embed_model = SentenceTransformerEncoder(model_name="/home/lyz/Rag/models/bge-m3")
```
Alternatively, test a single recommendation in an interactive script:
```python
from recosystem.core import UserBusinessRecommender
from recosystem.demo import examples_demo

recommender = UserBusinessRecommender(
    db_config=db_config,
    api_key='',  # Optional, for external services if needed
    embed_model=embed_model
)

i = 0
result = recommender.recommend(username=examples_demo[i][1], query=examples_demo[i][0])
print("[推荐结果]：")
print(result)
```
## 🧪 Running the System

You can run the main pipeline by executing:

```bash
python main.py


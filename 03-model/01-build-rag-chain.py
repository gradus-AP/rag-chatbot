# Databricks notebook source
# ========================================
# RAGチェーン構築（Databricks SDK + LangChain Community）
# ========================================

# COMMAND ----------

%pip install databricks-vectorsearch langchain-community mlflow --quiet
dbutils.library.restartPython()

# COMMAND ----------

%run ../00-config

# COMMAND ----------

import os
from databricks.vector_search.client import VectorSearchClient
from langchain_community.llms import Databricks

# 認証設定
DATABRICKS_TOKEN = dbutils.secrets.get(SECRET_SCOPE, SECRET_KEY)
os.environ['DATABRICKS_TOKEN'] = DATABRICKS_TOKEN
os.environ['DATABRICKS_HOST'] = HOST

print("✅ 環境変数設定完了")

# COMMAND ----------

# Vector Search クライアント
vsc = VectorSearchClient(
    workspace_url=HOST,
    personal_access_token=DATABRICKS_TOKEN
)

vs_index = vsc.get_index(
    endpoint_name=VECTOR_SEARCH_ENDPOINT,
    index_name=VECTOR_INDEX_NAME
)

print("✅ Vector Search接続完了")

# COMMAND ----------

# LLM初期化
llm = Databricks(
    endpoint_name=LLM_ENDPOINT,
    model_kwargs={"temperature": 0.1, "max_tokens": 500}
)

print(f"✅ LLMモデル接続完了: {LLM_ENDPOINT}")

# COMMAND ----------

# RAG関数
def ask_question(question: str, num_results: int = 3) -> str:
    """質問に対してRAGで回答を生成"""

    # 1. Vector Searchで関連文書を検索
    search_results = vs_index.similarity_search(
        query_text=question,
        columns=["content", "url"],
        num_results=num_results
    )

    # 2. 検索結果から文書を抽出
    documents = search_results.get('result', {}).get('data_array', [])

    if not documents:
        return "関連する情報が見つかりませんでした。"

    # 3. コンテキストを構築
    context = "\n\n".join([doc[0] for doc in documents])

    # 4. プロンプトを作成
    prompt = f"""以下の情報を使って質問に日本語で簡潔に答えてください。
答えがわからない場合は「わかりません」と答えてください。

情報:
{context}

質問: {question}

回答:"""

    # 5. LLMを呼び出し
    answer = llm(prompt)

    return answer

print("✅ RAG関数定義完了")

# COMMAND ----------

# 簡易テスト
print("\n🧪 簡易動作確認...")

test_questions = [
    "Databricksとは？",
    "サンプル文書について教えて"
]

for q in test_questions:
    print(f"\n質問: {q}")
    answer = ask_question(q)
    print(f"回答: {answer}")
    print("-" * 60)

print("\n✅ RAG動作確認完了")

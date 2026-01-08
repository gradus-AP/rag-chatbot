# Databricks notebook source
# ========================================
# RAGチェーン構築
# ========================================

# COMMAND ----------

%pip install --upgrade databricks-langchain langchain-community langchain>=0.3.0 langchain-core>=0.3.0 databricks-sql-connector databricks-vectorsearch mlflow --quiet
dbutils.library.restartPython()

# COMMAND ----------

%run ../00-config

# COMMAND ----------

import os
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatDatabricks
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.embeddings import DatabricksEmbeddings
from databricks.vector_search.client import VectorSearchClient

# 認証設定
os.environ['DATABRICKS_TOKEN'] = dbutils.secrets.get(SECRET_SCOPE, SECRET_KEY)
os.environ["DATABRICKS_HOST"] = HOST

print("✅ 環境変数設定完了")

# COMMAND ----------

# Retriever構築
def get_retriever():
    '''Vector Searchベースのretrieverを返す'''
    vsc = VectorSearchClient(
        workspace_url=HOST,
        personal_access_token=os.environ["DATABRICKS_TOKEN"]
    )
    vs_index = vsc.get_index(
        endpoint_name=VECTOR_SEARCH_ENDPOINT,
        index_name=VECTOR_INDEX_NAME
    )
    embedding = DatabricksEmbeddings(endpoint=EMBEDDING_MODEL_ENDPOINT)
    vectorstore = DatabricksVectorSearch(
        vs_index,
        text_column="content",
        embedding=embedding
    )
    return vectorstore.as_retriever()

print("✅ Retriever関数定義完了")

# COMMAND ----------

# プロンプトテンプレート
TEMPLATE = """以下の情報を使って質問に日本語で簡潔に答えてください。
答えがわからない場合は「わかりません」と答えてください。

情報:
{context}

質問: {question}

回答:"""

prompt = PromptTemplate(template=TEMPLATE, input_variables=["context", "question"])

print("✅ プロンプトテンプレート作成完了")

# COMMAND ----------

# LLMモデル
chat_model = ChatDatabricks(endpoint=LLM_ENDPOINT, max_tokens=500)

print(f"✅ LLMモデル接続完了: {LLM_ENDPOINT}")

# COMMAND ----------

# RAGチェーン作成
rag_chain = RetrievalQA.from_chain_type(
    llm=chat_model,
    chain_type="stuff",
    retriever=get_retriever(),
    chain_type_kwargs={"prompt": prompt}
)

print("✅ RAGチェーン構築完了")

# COMMAND ----------

# 簡易テスト
print("\n🧪 簡易動作確認...")

test_questions = [
    "Databricksとは？",
    "サンプル文書について教えて"
]

for q in test_questions:
    print(f"\n質問: {q}")
    result = rag_chain.run({"query": q})
    print(f"回答: {result}")
    print("-" * 60)

print("\n✅ RAGチェーン動作確認完了")
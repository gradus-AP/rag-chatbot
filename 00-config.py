# Databricks notebook source
# ========================================
# 中央設定ファイル
# ========================================

# 環境切り替え
ENV = "dev"  # "dev" | "staging" | "prod"

# Unity Catalog
CATALOG = f"rag_demo_{ENV}"
SCHEMA = "chatbot"

# Endpoints
VECTOR_SEARCH_ENDPOINT = f"vs_endpoint_{ENV}"
# Databricks Foundation Model API のエンドポイント名
# 利用可能なモデル: databricks-bge-large-en, databricks-gte-large-en など
EMBEDDING_MODEL_ENDPOINT = "databricks-bge-large-en"  # Embedding model
LLM_ENDPOINT = "databricks-dbrx-instruct"  # LLM model

# 命名規則
def get_table_name(name):
    return f"{CATALOG}.{SCHEMA}.{name}"

def get_model_name(name):
    return f"{CATALOG}.{SCHEMA}.{name}"

# テーブル
RAW_DOCS_TABLE = get_table_name("raw_documents")
CHUNKED_DOCS_TABLE = get_table_name("chunked_documents")
VECTOR_INDEX_NAME = get_table_name("docs_vector_index")

# モデル
MODEL_NAME = get_model_name("rag_chatbot")
SERVING_ENDPOINT_NAME = f"rag_endpoint_{ENV}"

# シークレット
SECRET_SCOPE = f"rag_demo_{ENV}"
SECRET_KEY = "api_token"

# チャンク設定
CHUNK_CONFIG = {
    "max_size": 500,
    "overlap": 50,
    "min_size": 20
}

# その他
HOST = "https://" + spark.conf.get("spark.databricks.workspaceUrl")

print(f"✅ 設定読み込み完了 [ENV: {ENV}]")
print(f"   Catalog: {CATALOG}")
print(f"   Schema: {SCHEMA}")
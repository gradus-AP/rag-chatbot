# Databricks notebook source
# ========================================
# Vector Index作成（冪等性保証）
# ========================================

# COMMAND ----------

%run ../00-config

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient
import time

vsc = VectorSearchClient()

# COMMAND ----------

# Index作成または同期
print(f"🔍 Vector Index処理中: {VECTOR_INDEX_NAME}")

try:
    # 既存Index取得を試みる
    index = vsc.get_index(VECTOR_SEARCH_ENDPOINT, VECTOR_INDEX_NAME)
    print("⚠️  Index既存 - 同期を実行")
    index.sync()
    action = "synced"
    
except Exception as e:
    if "NOT_FOUND" in str(e) or "RESOURCE_DOES_NOT_EXIST" in str(e):
        # Index作成
        print("🆕 新規Index作成中...")
        vsc.create_delta_sync_index(
            endpoint_name=VECTOR_SEARCH_ENDPOINT,
            index_name=VECTOR_INDEX_NAME,
            source_table_name=CHUNKED_DOCS_TABLE,
            pipeline_type="TRIGGERED",
            primary_key="id",
            embedding_source_column="content",
            embedding_model_endpoint_name=EMBEDDING_MODEL_ENDPOINT
        )
        action = "created"
    else:
        raise

print(f"✅ Index {action}")

# COMMAND ----------

# Index準備待機
print("⏳ Index準備中...")
max_wait = 600
start_time = time.time()

while time.time() - start_time < max_wait:
    try:
        index = vsc.get_index(VECTOR_SEARCH_ENDPOINT, VECTOR_INDEX_NAME)
        status = index.describe()
        
        if status.get("status", {}).get("ready"):
            print("✅ Index準備完了！")
            break
        
        elapsed = int(time.time() - start_time)
        print(f"   待機中... ({elapsed}秒経過)")
        time.sleep(10)
    except:
        time.sleep(10)
else:
    print("⚠️  タイムアウト - 手動で確認してください")

# COMMAND ----------

# テスト検索
print("\n🔍 テスト検索実行...")

test_queries = [
    "Databricksとは？",
    "Sparkについて教えて",
    "サンプル文書"
]

for query in test_queries:
    print(f"\n質問: {query}")
    results = vsc.get_index(VECTOR_SEARCH_ENDPOINT, VECTOR_INDEX_NAME).similarity_search(
        query_text=query,
        columns=["url", "content"],
        num_results=2
    )
    
    for i, doc in enumerate(results.get('result', {}).get('data_array', []), 1):
        print(f"  {i}. {doc[0]}")
        print(f"     {doc[1][:80]}...")

print("\n✅ Vector Index準備完了！")
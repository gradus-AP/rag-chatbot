# Databricks notebook source
# ========================================
# 環境検証（冪等性保証）
# ========================================

# COMMAND ----------

# 必要なパッケージをインストール
%pip install databricks-vectorsearch --quiet

# COMMAND ----------

# Pythonカーネルの再起動（パッケージを有効化するため）
dbutils.library.restartPython()

# COMMAND ----------

%run ../00-config

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

def validate_or_create():
    '''環境を検証し、必要に応じて作成'''

    results = {
        "catalog": False,
        "schema": False,
        "vector_endpoint": False,
        "secrets": False
    }

    # Catalog
    try:
        spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
        spark.sql(f"USE CATALOG {CATALOG}")
        results["catalog"] = True
        print(f"✅ Catalog: {CATALOG}")
    except Exception as e:
        print(f"❌ Catalog error: {e}")

    # Schema
    try:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
        results["schema"] = True
        print(f"✅ Schema: {SCHEMA}")
    except Exception as e:
        print(f"❌ Schema error: {e}")

    # Vector Search Endpoint
    try:
        vsc = VectorSearchClient()
        endpoint_list = vsc.list_endpoints().get('endpoints', [])

        # endpointがdictの場合とオブジェクトの場合に対応
        if endpoint_list:
            if isinstance(endpoint_list[0], dict):
                endpoints = [e.get('name') for e in endpoint_list]
            else:
                endpoints = [e.name for e in endpoint_list]
        else:
            endpoints = []

        if VECTOR_SEARCH_ENDPOINT in endpoints:
            results["vector_endpoint"] = True
            print(f"✅ Vector Endpoint: {VECTOR_SEARCH_ENDPOINT}")
        else:
            print(f"⚠️  Vector Endpoint not found: {VECTOR_SEARCH_ENDPOINT}")
            print(f"   手動で作成してください:")
            print(f"   1. Databricks UI → Compute → Vector Search")
            print(f"   2. 'Create Endpoint' をクリック")
            print(f"   3. Name: {VECTOR_SEARCH_ENDPOINT}")
            print(f"   4. Type: Standard を選択")
    except Exception as e:
        print(f"❌ Vector Endpoint error: {e}")
    
    # Secrets
    try:
        dbutils.secrets.get(SECRET_SCOPE, SECRET_KEY)
        results["secrets"] = True
        print(f"✅ Secrets: {SECRET_SCOPE}/{SECRET_KEY}")
    except:
        print(f"⚠️  Secrets not found: {SECRET_SCOPE}/{SECRET_KEY}")
        print(f"   Run: databricks secrets create-scope {SECRET_SCOPE}")
        print(f"   Run: databricks secrets put-secret {SECRET_SCOPE} {SECRET_KEY}")
    
    # 結果サマリー
    print("\n" + "="*60)
    all_ok = all(results.values())
    if all_ok:
        print("🎉 すべての検証に成功！")
    else:
        print("⚠️  一部の検証に失敗 - 上記メッセージを確認してください")
    print("="*60)
    
    return results

# COMMAND ----------

validation_results = validate_or_create()
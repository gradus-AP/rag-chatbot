# Databricks notebook source
# ========================================
# モデルデプロイ（冪等性保証）
# ========================================

# COMMAND ----------

%run ../00-config

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import (
    EndpointCoreConfigInput,
    ServedModelInput,
    ServedModelInputWorkloadSize
)
import mlflow

mlflow.set_registry_uri("databricks-uc")
w = WorkspaceClient()

# COMMAND ----------

# 最新バージョン取得
print(f"📦 モデル情報取得中: {MODEL_NAME}")

client = mlflow.MlflowClient()

# Unity Catalog対応: バージョン一覧から最新を取得
try:
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")

    if not versions:
        raise Exception(f"❌ モデルが見つかりません: {MODEL_NAME}\n   先に 02-test-and-register を実行してください")

    # バージョン番号でソート（降順）して最新を取得
    latest_version = max([int(v.version) for v in versions])
    print(f"✅ 最新バージョン: v{latest_version}")

except Exception as e:
    raise Exception(f"❌ モデル取得エラー: {e}\n   先に 02-test-and-register を実行してください")

# COMMAND ----------

# エンドポイント設定
print(f"\n🚀 エンドポイント設定: {SERVING_ENDPOINT_NAME}")

endpoint_config = EndpointCoreConfigInput(
    served_models=[
        ServedModelInput(
            model_name=MODEL_NAME,
            model_version=str(latest_version),
            workload_size=ServedModelInputWorkloadSize.SMALL,
            scale_to_zero_enabled=True,
            environment_vars={
                "VECTOR_SEARCH_ENDPOINT": VECTOR_SEARCH_ENDPOINT,
                "VECTOR_INDEX_NAME": VECTOR_INDEX_NAME,
                "LLM_ENDPOINT": LLM_ENDPOINT,
                "DATABRICKS_HOST": HOST,
                "DATABRICKS_TOKEN": "{{secrets/" + SECRET_SCOPE + "/" + SECRET_KEY + "}}"
            }
        )
    ]
)

print("✅ 設定完了")

# COMMAND ----------

# デプロイ実行（冪等性保証）
print(f"\n🔄 デプロイ実行中...")

# 強制再作成モード（エラー時に有効化）
FORCE_RECREATE = True  # True にすると既存エンドポイントを削除して再作成

existing = next(
    (e for e in w.serving_endpoints.list() if e.name == SERVING_ENDPOINT_NAME),
    None
)

try:
    if existing:
        if FORCE_RECREATE:
            print(f"🗑️  既存エンドポイント削除: {SERVING_ENDPOINT_NAME}")
            w.serving_endpoints.delete(SERVING_ENDPOINT_NAME)
            import time
            time.sleep(10)  # 削除完了を待機

            print(f"🆕 新規エンドポイント作成: {SERVING_ENDPOINT_NAME}")
            w.serving_endpoints.create_and_wait(
                name=SERVING_ENDPOINT_NAME,
                config=endpoint_config
            )
            action = "再作成"
        else:
            print(f"♻️  既存エンドポイント更新: {SERVING_ENDPOINT_NAME}")

            # 現在の状態を確認
            current_state = w.serving_endpoints.get(SERVING_ENDPOINT_NAME)
            print(f"   現在の状態: {current_state.state}")

            w.serving_endpoints.update_config_and_wait(
                name=SERVING_ENDPOINT_NAME,
                served_models=endpoint_config.served_models
            )
            action = "更新"
    else:
        print(f"🆕 新規エンドポイント作成: {SERVING_ENDPOINT_NAME}")
        w.serving_endpoints.create_and_wait(
            name=SERVING_ENDPOINT_NAME,
            config=endpoint_config
        )
        action = "作成"

    print(f"✅ エンドポイント{action}完了！")

except Exception as e:
    print(f"\n❌ デプロイ失敗: {e}")

    # 詳細なエラー情報を取得
    try:
        endpoint = w.serving_endpoints.get(SERVING_ENDPOINT_NAME)
        print(f"\n📊 エンドポイント状態:")
        print(f"   State: {endpoint.state}")

        if endpoint.state and endpoint.state.config_update:
            print(f"   Config Update: {endpoint.state.config_update}")

        # Pending configの確認
        if hasattr(endpoint, 'pending_config') and endpoint.pending_config:
            print(f"\n⏳ Pending Config:")
            print(f"   {endpoint.pending_config}")

        # Tagsの確認
        if hasattr(endpoint, 'tags') and endpoint.tags:
            print(f"\n🏷️  Tags:")
            for tag in endpoint.tags:
                print(f"   {tag.key}: {tag.value}")

    except Exception as detail_error:
        print(f"詳細情報の取得に失敗: {detail_error}")

    print(f"\n💡 解決方法:")
    print(f"   1. FORCE_RECREATE = True に設定して再実行")
    print(f"   2. または UI で手動削除: Serving → {SERVING_ENDPOINT_NAME} → Delete")

    raise

# COMMAND ----------

# デプロイメントテスト
print(f"\n🧪 デプロイメントテスト実行中...")

test_queries = [
    "Databricksとは？",
    "Sparkの特徴は？",
    "サンプル文書について"
]

print("="*60)

for q in test_queries:
    print(f"\n質問: {q}")
    try:
        response = w.serving_endpoints.query(
            SERVING_ENDPOINT_NAME,
            dataframe_records=[{"query": q}]
        )
        answer = response.predictions[0]
        print(f"回答: {answer}")
        print("✅ 成功")
    except Exception as e:
        print(f"❌ エラー: {e}")
    print("-" * 60)

print("\n✅ デプロイメントテスト完了！")

# COMMAND ----------

displayHTML(f"""
<div style="padding: 20px; background-color: #e8f5e9; border-radius: 10px;">
<h2>🎉 デプロイ完了！</h2>
<p><strong>エンドポイント名:</strong> {SERVING_ENDPOINT_NAME}</p>
<p><strong>モデル:</strong> {MODEL_NAME} v{latest_version}</p>
<p><strong>環境:</strong> {ENV}</p>

<h3>次のステップ:</h3>
<ul>
  <li><a href="/ml/endpoints/{SERVING_ENDPOINT_NAME}" target="_blank">📡 エンドポイントを確認</a></li>
  <li><code>04-app/streamlit_app.py</code> でUIを起動</li>
</ul>

<h3>エンドポイント使用例:</h3>
<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
import requests

url = "https://your-workspace.cloud.databricks.com/serving-endpoints/{SERVING_ENDPOINT_NAME}/invocations"
headers = {{"Authorization": "Bearer YOUR_TOKEN"}}
data = {{"dataframe_records": [{{"query": "質問"}}]}}

response = requests.post(url, headers=headers, json=data)
print(response.json()["predictions"][0])
</pre>
</div>
""")
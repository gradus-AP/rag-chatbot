# Databricks notebook source
# ========================================
# モデルデプロイ（冪等性保証）
# ========================================

# COMMAND ----------

%run ../00-config

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedModelInput
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
            workload_size="Small",
            scale_to_zero_enabled=True
        )
    ]
)

print("✅ 設定完了")

# COMMAND ----------

# デプロイ実行（冪等性保証）
print(f"\n🔄 デプロイ実行中...")

existing = next(
    (e for e in w.serving_endpoints.list() if e.name == SERVING_ENDPOINT_NAME),
    None
)

if existing:
    print(f"♻️  既存エンドポイント更新: {SERVING_ENDPOINT_NAME}")
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
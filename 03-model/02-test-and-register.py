# Databricks notebook source
# ========================================
# テスト + MLflow登録
# ========================================

# COMMAND ----------

%run ./01-build-rag-chain

# COMMAND ----------

# テストケース実行
test_cases = [
    {
        "query": "Databricksとは？",
        "expected_keywords": ["Databricks", "データ", "プラットフォーム"]
    },
    {
        "query": "Sparkについて教えて",
        "expected_keywords": ["Spark", "Apache"]
    },
    {
        "query": "サンプル文書の内容は？",
        "expected_keywords": ["サンプル", "文書"]
    }
]

print("🧪 テスト実行中...\n")
print("="*60)

results = []

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['query']}")
    
    try:
        answer = rag_chain.run({"query": test["query"]})
        print(f"回答: {answer}")
        
        # キーワードチェック
        found = [kw for kw in test["expected_keywords"] if kw in answer]
        
        if found:
            print(f"✅ PASS (キーワード: {', '.join(found)})")
            results.append(True)
        else:
            print(f"⚠️  WARNING (期待キーワードなし: {', '.join(test['expected_keywords'])})")
            results.append(False)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append(False)
    
    print("-" * 60)

passed = sum(results)
print(f"\n結果: {passed}/{len(test_cases)} passed")

# COMMAND ----------

# MLflow登録
import mlflow
from mlflow.models import infer_signature

mlflow.set_registry_uri("databricks-uc")

print(f"\n📦 MLflowにモデル登録中...")
print(f"   モデル名: {MODEL_NAME}")

# シグネチャ作成
question = {"query": "Databricksとは？"}
answer = rag_chain.run(question)
signature = infer_signature(question, answer)

# COMMAND ----------

# モデル登録
with mlflow.start_run(run_name=f"rag_chatbot_{ENV}") as run:
    model_info = mlflow.langchain.log_model(
        rag_chain,
        loader_fn=get_retriever,
        artifact_path="chain",
        registered_model_name=MODEL_NAME,
        pip_requirements=[
            "mlflow",
            "langchain",
            "databricks-vectorsearch"
        ],
        input_example=question,
        signature=signature
    )
    
    print(f"✅ モデル登録完了: {MODEL_NAME}")
    print(f"   Run ID: {run.info.run_id}")
    print(f"   Version: {model_info.registered_model_version}")

# COMMAND ----------

displayHTML(f"""
<div style="padding: 20px; background-color: #e8f5e9; border-radius: 10px;">
<h2>✅ モデル登録完了！</h2>
<p><strong>モデル名:</strong> {MODEL_NAME}</p>
<p><strong>バージョン:</strong> {model_info.registered_model_version}</p>
<p><a href="#mlflow/models/{MODEL_NAME}" target="_blank">📊 モデルを確認</a></p>
<p>次は <code>03-model/03-deploy</code> を実行してください</p>
</div>
""")
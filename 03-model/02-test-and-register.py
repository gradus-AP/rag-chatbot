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
        answer = ask_question(test["query"])
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
from mlflow.pyfunc import PythonModel

mlflow.set_registry_uri("databricks-uc")

print(f"\n📦 MLflowにモデル登録中...")
print(f"   モデル名: {MODEL_NAME}")

# COMMAND ----------

# カスタムPyFuncモデルでラップ
class RAGChatbot(PythonModel):
    """RAG Chatbot MLflow wrapper"""

    def load_context(self, context):
        """モデルコンテキストをロード"""
        import os
        from databricks.vector_search.client import VectorSearchClient
        from databricks_langchain import ChatDatabricks

        # 環境変数から設定を読み込み
        self.vector_search_endpoint = os.environ.get('VECTOR_SEARCH_ENDPOINT')
        self.vector_index_name = os.environ.get('VECTOR_INDEX_NAME')
        self.llm_endpoint = os.environ.get('LLM_ENDPOINT')
        self.host = os.environ.get('DATABRICKS_HOST')
        self.token = os.environ.get('DATABRICKS_TOKEN')

        # Vector Search接続
        self.vsc = VectorSearchClient(
            workspace_url=self.host,
            personal_access_token=self.token
        )
        self.vs_index = self.vsc.get_index(
            endpoint_name=self.vector_search_endpoint,
            index_name=self.vector_index_name
        )

        # LLM初期化
        self.llm = ChatDatabricks(
            endpoint=self.llm_endpoint,
            temperature=0.1,
            max_tokens=500
        )

    def predict(self, context, model_input):
        """質問に対して回答を生成"""
        # model_inputはDataFrameまたはdict
        if hasattr(model_input, 'to_dict'):
            questions = model_input.to_dict('records')
        else:
            questions = [model_input] if isinstance(model_input, dict) else model_input

        answers = []
        for item in questions:
            question = item.get('query') or item.get('question')

            # Vector Search
            search_results = self.vs_index.similarity_search(
                query_text=question,
                columns=["content", "url"],
                num_results=3
            )

            # コンテキスト構築
            documents = search_results.get('result', {}).get('data_array', [])
            if not documents:
                answers.append("関連する情報が見つかりませんでした。")
                continue

            context_text = "\n\n".join([doc[0] for doc in documents])

            # プロンプト作成
            prompt = f"""以下の情報を使って質問に日本語で簡潔に答えてください。
答えがわからない場合は「わかりません」と答えてください。

情報:
{context_text}

質問: {question}

回答:"""

            # LLM呼び出し
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            answers.append(answer)

        return answers

# COMMAND ----------

# シグネチャ作成
question_input = {"query": "Databricksとは？"}
test_answer = ask_question(question_input["query"])
signature = infer_signature(question_input, test_answer)

# COMMAND ----------

# 環境変数を設定（モデルが使用）
import os
os.environ['VECTOR_SEARCH_ENDPOINT'] = VECTOR_SEARCH_ENDPOINT
os.environ['VECTOR_INDEX_NAME'] = VECTOR_INDEX_NAME
os.environ['LLM_ENDPOINT'] = LLM_ENDPOINT

# モデル登録
with mlflow.start_run(run_name=f"rag_chatbot_{ENV}") as run:
    model_info = mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=RAGChatbot(),
        registered_model_name=MODEL_NAME,
        pip_requirements=[
            "mlflow",
            "databricks-vectorsearch",
            "databricks-langchain"
        ],
        input_example=question_input,
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

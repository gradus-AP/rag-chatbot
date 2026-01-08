# エラー対応メモ

## 発生したエラーと解決策

### 1. ModuleNotFoundError: No module named 'langchain.text_splitter'

**エラー内容:**
```
ModuleNotFoundError: No module named 'langchain.text_splitter'
```

**原因:**
- パッケージインストールの順序が間違っていた
- `%run ../00-config` → `%pip install` → `dbutils.library.restartPython()` の順序
- `restartPython()` でPythonカーネルが再起動され、configで読み込んだ内容が消える

**解決策:**
- パッケージインストール順序を変更: `%pip install` → `dbutils.library.restartPython()` → `%run ../00-config`
- CODE_REVIEW_CHECKLIST.md の NB-012 に準拠

**修正コミット:**
- `78ad38a` Fix LangChain import error by reordering package installation

**参考:**
- [CODE_REVIEW_CHECKLIST.md:70](CODE_REVIEW_CHECKLIST.md#L70) - NB-012

---

### 2. 'dict' object has no attribute 'name' (Vector Endpoint Validation)

**エラー内容:**
```
❌ Vector Endpoint error: 'dict' object has no attribute 'name'
```

**原因:**
- `VectorSearchClient.list_endpoints()` のレスポンス形式が想定と異なる
- レスポンスが dict のリストだったが、オブジェクトのリストを想定していた

**解決策:**
- `isinstance()` で dict かオブジェクトかを判定
- dict の場合: `e.get('name')` でアクセス
- オブジェクトの場合: `e.name` でアクセス

**修正コミット:**
- `51e29f4` Fix Vector Endpoint validation to handle dict responses

**修正箇所:**
```python
# 修正前
endpoints = [e.name for e in vsc.list_endpoints().get('endpoints', [])]

# 修正後
endpoint_list = vsc.list_endpoints().get('endpoints', [])
if endpoint_list:
    if isinstance(endpoint_list[0], dict):
        endpoints = [e.get('name') for e in endpoint_list]
    else:
        endpoints = [e.name for e in endpoint_list]
else:
    endpoints = []
```

---

### 3. Langchain Dependency Conflicts

**エラー内容:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
langgraph-checkpoint 3.1 requires langchain-core>=0.2.38, but you have langchain-core 0.1.23 which is incompatible.
```

**原因:**
- langchain のバージョンが古すぎる (0.1.23)
- langgraph-checkpoint が langchain-core>=0.2.38 を要求

**解決策:**
- langchain のバージョンを明示的に指定: `langchain>=0.3.0`
- langchain-core も同様: `langchain-core>=0.3.0`

**修正コミット:**
- `549e79a` Fix langchain dependency conflicts with version constraints

**修正箇所:**
```python
# 修正前
%pip install langchain databricks-vectorsearch mlflow --quiet

# 修正後
%pip install langchain>=0.3.0 langchain-core>=0.3.0 langchain-community databricks-vectorsearch mlflow --quiet
```

---

### 4. EnvironmentError: Failed to set environment metadata

**エラー内容:**
```
EnvironmentError: Failed to set environment metadata. The Spark session may be unavailable, please try again or contact Databricks support.
```

**原因:**
- `%pip install` がSpark設定 (`spark.conf.set`) にアクセスできない
- クラスターの状態が不安定
- 一時的なDatabricksの問題

**試した解決策:**
1. ❌ クラスター再起動 - 解決せず
2. ❌ 環境変数設定 - 解決せず
3. ❌ クラスターレベルでのライブラリインストール - サーバーレスでは使えない
4. ✅ **何もしない** - エラーは出るが実際には動作する

**ワークアラウンド:**
- 全て実行 → 失敗
- クラスター停止
- 全て実行（もう一度）→ 成功

**結論:**
- このエラーは無視して問題なし
- サーバーレスコンピュートでは2回実行すれば成功する

---

### 5. protobuf dependency warning (非致命的)

**エラー内容:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
grpcio-status 1.69.0 requires protobuf<6.0dev,>=5.26.1, but you have protobuf 4.25.8 which is incompatible.
```

**原因:**
- grpcio-status が protobuf>=5.26.1 を要求
- インストールされているのは protobuf 4.25.8

**対応:**
- ⚠️ **WARNING なので無視してOK**
- 実際の動作に影響なし
- 必要に応じて `protobuf>=5.26.1` を追加可能

**対応方法 (オプション):**
```python
%pip install databricks-vectorsearch protobuf>=5.26.1 --quiet
```

---

### 6. ModuleNotFoundError: No module named 'langchain.chains'

**エラー内容:**
```
ModuleNotFoundError: No module named 'langchain.chains'
```

**原因:**
- LangChain 0.3.x で `langchain.chains` モジュールが削除または再構成された
- 従来の `RetrievalQA.from_chain_type()` などが使えなくなった
- LangChain 0.3.x では LCEL (LangChain Expression Language) への移行が推奨される

**試した解決策:**
1. ❌ `from langchain.chains.retrieval_qa.base import RetrievalQA` - モジュール見つからず
2. ❌ LCEL への移行 - 複雑すぎる
3. ✅ **LangChain chains を完全に諦める**

**最終解決策:**
- LangChain の複雑なチェーン機構を使わず、シンプルな実装に変更
- `databricks-langchain` パッケージの `ChatDatabricks` を直接使用
- RAGロジックを手動で実装: Vector Search → Context構築 → LLM呼び出し

**修正コミット:**
- `ccebb53` Migrate to LangChain 0.3.x retrieval chain API (失敗)
- `0cc5dfd` Abandon LangChain chains, use simple Databricks SDK approach (成功)

**修正前 (LangChain chains):**
```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
```

**修正後 (シンプルな実装):**
```python
from databricks_langchain import ChatDatabricks

llm = ChatDatabricks(
    endpoint=LLM_ENDPOINT,
    temperature=0.1,
    max_tokens=500
)

def ask_question(question: str, num_results: int = 3) -> str:
    # 1. Vector Search
    search_results = vs_index.similarity_search(
        query_text=question,
        columns=["content", "url"],
        num_results=num_results
    )

    # 2. コンテキスト構築
    documents = search_results.get('result', {}).get('data_array', [])
    context = "\n\n".join([doc[0] for doc in documents])

    # 3. プロンプト作成
    prompt = f"""以下の情報を使って質問に日本語で簡潔に答えてください。

情報:
{context}

質問: {question}

回答:"""

    # 4. LLM呼び出し
    response = llm.invoke(prompt)
    return response.content if hasattr(response, 'content') else str(response)
```

**学び:**
- ✅ LangChain 0.3.x は複雑すぎる → Databricks公式パッケージで十分
- ✅ `databricks-langchain` + `databricks-vectorsearch` でシンプルに実装可能
- ✅ RAGロジックは手動実装の方が制御しやすい

**参考:**
- [databricks-langchain Documentation](https://github.com/databricks/databricks-langchain)

---

### 7. LangChainDeprecationWarning: langchain_community.llms.Databricks deprecated

**エラー内容:**
```
LangChainDeprecationWarning: The class `Databricks` was deprecated in LangChain 0.3.8 and will be removed in 1.0.0. An updated version of the class exists in the :class:`~databricks-langchain package and should be used instead.
```

**原因:**
- `langchain_community.llms.Databricks` が非推奨になった
- LangChain 0.3.8 以降は `databricks-langchain` パッケージへ移行

**解決策:**
- `langchain_community` から `databricks_langchain` への移行
- パッケージインストール: `%pip install databricks-langchain`

**修正コミット:**
- `a08576e` Migrate from langchain_community to databricks-langchain

**修正前:**
```python
from langchain_community.llms import Databricks

llm = Databricks(
    endpoint_name=LLM_ENDPOINT,
    model_kwargs={"temperature": 0.1, "max_tokens": 500}
)

answer = llm(prompt)
```

**修正後:**
```python
from databricks_langchain import ChatDatabricks

llm = ChatDatabricks(
    endpoint=LLM_ENDPOINT,
    temperature=0.1,
    max_tokens=500
)

response = llm.invoke(prompt)
answer = response.content if hasattr(response, 'content') else str(response)
```

---

### 8. IllegalArgumentException: Secret does not exist

**エラー内容:**
```
IllegalArgumentException: Secret does not exist with scope: rag_demo_dev and key: api_token
```

**原因:**
- Secret Scope `rag_demo_dev` が作成されていない
- Databricks notebook 上では `dbutils.secrets.createScope()` は存在しない
- Secret Scope 作成には CLI または REST API が必要

**解決策:**
- Databricks CLI をインストールして Secret Scope を作成

**手順:**
```bash
# 1. Databricks CLI インストール
pip3 install databricks-cli

# 2. 認証設定
databricks configure --token
# Host: https://dbc-xxxx.cloud.databricks.com
# Token: dapi...

# 3. Secret Scope 作成
databricks secrets create-scope --scope rag_demo_dev

# 4. Secret 追加
databricks secrets put --scope rag_demo_dev --key api_token --string-value "dapi..."

# 5. 確認
databricks secrets list --scope rag_demo_dev
```

**注意:**
- ❌ UI での Secret Scope 作成は不可
- ❌ Notebook 上での `dbutils.secrets.createScope()` は存在しない
- ✅ CLI または REST API のみ対応

**参考:**
- [Databricks Secrets CLI Documentation](https://docs.databricks.com/en/security/secrets/secrets.html)

---

### 9. NotFoundError: databricks-dbrx-instruct endpoint not found

**エラー内容:**
```
NotFoundError: Error code: 404 - {'error_code': 'RESOURCE_DOES_NOT_EXIST', 'message': 'Failed to find MT LLM Endpoint for requested endpoint: databricks-dbrx-instruct'}
```

**原因:**
- `00-config.py` で指定した `LLM_ENDPOINT = "databricks-dbrx-instruct"` が存在しない
- エンドポイント名が間違っている、または利用可能でない

**確認方法:**
```python
# Databricks notebook で実行
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
endpoints = w.serving_endpoints.list()

print("利用可能なエンドポイント:")
for endpoint in endpoints:
    print(f"  - {endpoint.name}")
```

**または UI で確認:**
- Databricks Workspace → Serving → Serving endpoints

**よくある正しいエンドポイント名:**
- `databricks-meta-llama-3-1-70b-instruct`
- `databricks-meta-llama-3-1-405b-instruct`
- `databricks-mixtral-8x7b-instruct`

**解決策 (TODO):**
- 正しいエンドポイント名を確認後、`00-config.py` の `LLM_ENDPOINT` を修正

**ステータス:** 🔴 **未解決**

---

## 今日の学び (2026-01-08)

### 1. LangChain 0.3.x の複雑さは避けるべき
- ❌ LangChain chains: 複雑、非推奨、エラーが多い
- ✅ Databricks公式パッケージ: シンプル、安定、ドキュメント充実

### 2. RAG実装はシンプルに
```python
# ベストプラクティス
Vector Search → Context構築 → LLM prompt → Response
```

### 3. パッケージインストール順序は絶対厳守
```python
# 正しい順序
%pip install ... --quiet
dbutils.library.restartPython()
%run ../00-config
```

### 4. Secret Scope は CLI で作成
- ❌ UI: 不可
- ❌ Notebook: 不可
- ✅ CLI: `databricks secrets create-scope --scope <name>`

### 5. Databricks公式パッケージを使う
- `databricks-langchain` (LLM呼び出し)
- `databricks-vectorsearch` (Vector Search)
- `langchain_community` は非推奨

---

## 実行方法

### サーバーレスコンピュートでの実行手順

1. **初回実行:**
   - 「全て実行」をクリック
   - パッケージがインストールされ、一部エラーが出る可能性あり

2. **クラスター停止:**
   - クラスターを停止してクリーンな状態にする

3. **2回目実行:**
   - 「全て実行」をクリック
   - 正常に動作する

### 注意事項

- `dbutils.library.restartPython()` 後は必ず `%run ../00-config` を実行
- パッケージインストールは常に config 読み込みの**前**に行う
- protobuf の warning は無視してOK

---

## 関連ドキュメント

- [CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md) - コーディング規約
- [requirements.txt](requirements.txt) - 依存パッケージ一覧

---

**作成日:** 2026-01-07
**最終更新:** 2026-01-08

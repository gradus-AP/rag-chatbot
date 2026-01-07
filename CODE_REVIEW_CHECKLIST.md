# コードレビューチェックリスト - Databricks RAG Chatbot

## 📋 目次

1. [Databricksノートブック規約](#databricksノートブック規約)
2. [コーディング規約](#コーディング規約)
3. [設定管理規約](#設定管理規約)
4. [データパイプライン規約](#データパイプライン規約)
5. [MLOps規約](#mlops規約)
6. [セキュリティ規約](#セキュリティ規約)
7. [パフォーマンス規約](#パフォーマンス規約)
8. [ドキュメント規約](#ドキュメント規約)
9. [テスト規約](#テスト規約)
10. [トラブルシューティング](#トラブルシューティング)

---

## ✅ Databricksノートブック規約

### 📌 MAGICコマンド

- [ ] **NB-001**: 全ノートブックは `# Databricks notebook source` で開始する
- [ ] **NB-002**: セルの区切りは `# COMMAND ----------` を使用する
- [ ] **NB-003**: `%run` で設定ファイル（`00-config.py`）を読み込む
- [ ] **NB-004**: `%pip install` の後は必ず `dbutils.library.restartPython()` を呼び出す
- [ ] **NB-005**: Markdown説明には `# MAGIC %md` を使用する（コメントではなく）
- [ ] **NB-006**: 複雑なSQL文は `%sql` セルで記述する
- [ ] **NB-007**: `%run` のパスは相対パスを使用する（例: `../00-config`）

**例（良い）:**
```python
# Databricks notebook source
# MAGIC %md
# MAGIC # データ取得パイプライン
# MAGIC このノートブックはドキュメントを取得しチャンク化します。

# COMMAND ----------

%run ../00-config

# COMMAND ----------

%pip install langchain transformers
dbutils.library.restartPython()

# COMMAND ----------
```

**例（悪い）:**
```python
# データ取得パイプライン  # ❌ MAGIC未使用
# このノートブックはドキュメントを取得しチャンク化します。

import sys
sys.path.append("../")
from config import *  # ❌ %run未使用

!pip install langchain  # ❌ %pip未使用
# ❌ restartPython()なし
```

---

### 📌 依存関係管理

- [ ] **NB-008**: 必要なパッケージは各ノートブック冒頭で`%pip install`する
- [ ] **NB-009**: `%pip install`の後は必ず`dbutils.library.restartPython()`を呼び出す
- [ ] **NB-010**: パッケージインストールには`--quiet`オプションを使用する
- [ ] **NB-011**: `VectorSearchClient`を使用するノートブックには`databricks-vectorsearch`をインストールする
- [ ] **NB-012**: パッケージインストール後は`%run`で設定ファイルを読み込む（順序重要）

**例（良い）:**
```python
# Databricks notebook source
# COMMAND ----------

# 必要なパッケージをインストール
%pip install databricks-vectorsearch langchain --quiet

# COMMAND ----------

# Pythonカーネルの再起動（パッケージを有効化するため）
dbutils.library.restartPython()

# COMMAND ----------

%run ../00-config

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient
```

**例（悪い）:**
```python
# COMMAND ----------

%run ../00-config

# COMMAND ----------

# ❌ パッケージインストールが設定読み込み後
%pip install databricks-vectorsearch
# ❌ restartPython()なし

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient  # ❌ ImportError発生
```

---

### 📌 セル構成

- [ ] **NB-013**: 1セルは1つの論理的な処理単位とする（50行以内推奨）
- [ ] **NB-014**: セルの先頭にコメントで処理内容を記述する
- [ ] **NB-015**: 長い処理は複数セルに分割する
- [ ] **NB-016**: セルの実行順序に依存関係がある場合は明示する
- [ ] **NB-017**: 各セクションの前に見出しセル（`%md`）を配置する

**例（良い）:**
```python
# COMMAND ----------
# MAGIC %md
# MAGIC ## データ取得

# COMMAND ----------

# サンプルドキュメント生成
sample_docs = [...]
df = spark.createDataFrame(sample_docs)

# COMMAND ----------
# MAGIC %md
# MAGIC ## チャンク化

# COMMAND ----------

# LangChain TextSplitterの初期化
text_splitter = RecursiveCharacterTextSplitter(...)
```

---

### 📌 出力・表示

- [ ] **NB-018**: 重要な処理結果は `print()` で明示的に出力する
- [ ] **NB-019**: DataFrameの表示は `display()` を使用する（`show()` ではなく）
- [ ] **NB-020**: 成功メッセージには絵文字を使用（✅, 🎉, ✓など）
- [ ] **NB-021**: エラーメッセージには明確な記号を使用（❌, ✗など）
- [ ] **NB-022**: 処理進捗には適切な記号を使用（⏳, 🔍, 📦など）

**例（良い）:**
```python
print(f"✅ データを {RAW_DOCS_TABLE} に保存しました")
print(f"   レコード数: {df.count()}")
display(df.limit(5))
```

**例（悪い）:**
```python
df.write.saveAsTable(RAW_DOCS_TABLE)  # ❌ 出力なし
df.show()  # ❌ show()ではなくdisplay()
```

---

## ✅ コーディング規約

### 📌 命名規則

- [ ] **CD-001**: 定数は `UPPER_SNAKE_CASE` を使用する
- [ ] **CD-002**: 変数・関数は `lower_snake_case` を使用する
- [ ] **CD-003**: クラスは `PascalCase` を使用する
- [ ] **CD-004**: プライベート変数・関数は `_` プレフィックスを使用する
- [ ] **CD-005**: 環境変数は意味のある名前を使用する（`TOKEN`、`ENDPOINT_URL`など）

**例:**
```python
# ✅ 良い
CATALOG = "rag_demo_dev"
CHUNK_CONFIG = {"max_size": 500}

def chunk_text(text: str) -> list:
    pass

class RAGChatbot:
    def _load_retriever(self):
        pass

# ❌ 悪い
catalog = "rag_demo_dev"  # 定数なのに小文字
ChunkConfig = {}          # 辞書なのにPascalCase
def ChunkText():          # 関数なのにPascalCase
```

---

### 📌 型ヒント

- [ ] **CD-006**: 関数の引数と戻り値には型ヒントを使用する
- [ ] **CD-007**: 複雑な型は `typing` モジュールを使用する
- [ ] **CD-008**: Pandas UDFには必ず型ヒントを記述する

**例（良い）:**
```python
from typing import List, Dict, Any

def chunk_text(text: str, max_size: int = 500) -> List[str]:
    """テキストをチャンクに分割"""
    return chunks

def get_config() -> Dict[str, Any]:
    """設定を返す"""
    return {"catalog": CATALOG, "schema": SCHEMA}

@pandas_udf("array<string>")
def chunk_udf(texts: pd.Series) -> pd.Series:
    return texts.apply(chunk_text)
```

**例（悪い）:**
```python
def chunk_text(text, max_size=500):  # ❌ 型ヒントなし
    return chunks

def get_config():  # ❌ 戻り値型なし
    return {"catalog": CATALOG}
```

---

### 📌 Docstring

- [ ] **CD-009**: 公開関数にはdocstringを記述する
- [ ] **CD-010**: docstringはGoogle形式またはNumPy形式を使用する
- [ ] **CD-011**: 複雑な処理はdocstringに処理フローを記述する
- [ ] **CD-012**: 日本語と英語を混在させない（どちらか統一）

**例（良い）:**
```python
def validate_or_create() -> Dict[str, bool]:
    """
    環境を検証し、必要に応じて作成する

    Returns:
        Dict[str, bool]: 検証結果の辞書
            - catalog: カタログの存在確認結果
            - schema: スキーマの存在確認結果
            - vector_endpoint: Vector Endpointの存在確認結果
            - secrets: Secretsの存在確認結果

    Examples:
        >>> results = validate_or_create()
        >>> if all(results.values()):
        >>>     print("環境準備完了")
    """
    results = {}
    # ... 処理 ...
    return results
```

---

### 📌 エラーハンドリング

- [ ] **CD-013**: `try-except` ブロックは具体的な例外型を指定する
- [ ] **CD-014**: 例外メッセージには文脈情報を含める
- [ ] **CD-015**: 回復可能なエラーは適切にハンドリングする
- [ ] **CD-016**: 回復不可能なエラーは `raise` で再送出する
- [ ] **CD-017**: 例外ログには十分な情報を含める

**例（良い）:**
```python
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
    print(f"✅ Catalog: {CATALOG}")
except AnalysisException as e:
    print(f"❌ Catalog作成エラー: {CATALOG}")
    print(f"   詳細: {str(e)}")
    raise
except Exception as e:
    print(f"❌ 予期しないエラー: {str(e)}")
    raise
```

**例（悪い）:**
```python
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
except:  # ❌ 例外型未指定
    print("エラー")  # ❌ 情報不足
    pass  # ❌ エラーを無視
```

---

### 📌 コード品質

- [ ] **CD-018**: マジックナンバーは定数化する
- [ ] **CD-019**: 重複コードは関数に抽出する
- [ ] **CD-020**: 1関数は1つの責務を持つ
- [ ] **CD-021**: ネストは3階層以内に抑える
- [ ] **CD-022**: 1行は120文字以内にする（PEP8推奨）

**例（良い）:**
```python
# 定数定義
MAX_RETRIES = 3
RETRY_INTERVAL = 10

def wait_for_index_ready(index_name: str,
                         max_retries: int = MAX_RETRIES) -> bool:
    """Index準備待機（単一責務）"""
    for i in range(max_retries):
        if is_index_ready(index_name):
            return True
        time.sleep(RETRY_INTERVAL)
    return False

def is_index_ready(index_name: str) -> bool:
    """Index準備状態確認（単一責務）"""
    index = vsc.get_index(index_name)
    return index.describe().get("status", {}).get("ready", False)
```

**例（悪い）:**
```python
# ❌ マジックナンバー、複数責務
def wait_for_index(name):
    for i in range(3):  # ❌ マジックナンバー
        try:
            index = vsc.get_index(name)
            if index.describe().get("status", {}).get("ready"):
                return True
            else:
                time.sleep(10)  # ❌ マジックナンバー
        except:
            pass
    return False
```

---

## ✅ 設定管理規約

### 📌 設定ファイル構成

- [ ] **CF-001**: 全設定は `00-config.py` に集約する
- [ ] **CF-002**: 環境ごとの設定は `ENV` 変数で切り替える
- [ ] **CF-003**: ハードコードされた値は禁止（全て設定ファイルから読み込む）
- [ ] **CF-004**: 設定変更後は全ノートブックを再実行する
- [ ] **CF-005**: 設定ファイルには必ず初期化成功メッセージを出力する

**例（良い - 00-config.py）:**
```python
# Databricks notebook source

# 環境切り替え
ENV = "dev"  # "dev" | "staging" | "prod"

# Unity Catalog
CATALOG = f"rag_demo_{ENV}"
SCHEMA = "chatbot"

# ... 他の設定 ...

# 初期化完了メッセージ
print(f"✅ 設定読み込み完了 [ENV: {ENV}]")
print(f"   Catalog: {CATALOG}")
print(f"   Schema: {SCHEMA}")
```

**例（悪い）:**
```python
# ❌ 各ノートブックに設定が散在
catalog = "rag_demo_dev"  # ノートブック1
catalog = "rag_demo_staging"  # ノートブック2（不整合）
```

---

### 📌 命名規則関数

- [ ] **CF-006**: テーブル名は `get_table_name()` 関数で生成する
- [ ] **CF-007**: モデル名は `get_model_name()` 関数で生成する
- [ ] **CF-008**: 環境プレフィックスは一貫性を保つ
- [ ] **CF-009**: 命名規則の変更は設定ファイルのみで行う

**例（良い）:**
```python
def get_table_name(name: str) -> str:
    """Unity Catalogテーブル名を生成"""
    return f"{CATALOG}.{SCHEMA}.{name}"

RAW_DOCS_TABLE = get_table_name("raw_documents")
CHUNKED_DOCS_TABLE = get_table_name("chunked_documents")
```

---

## ✅ データパイプライン規約

### 📌 Delta Lake操作

- [ ] **DP-001**: Delta Tableの書き込みは必ず `mode` を明示する
- [ ] **DP-002**: 冪等性を保証する（`overwrite` または `IF NOT EXISTS`）
- [ ] **DP-003**: Change Data Feedが必要な場合は明示的に有効化する
- [ ] **DP-004**: テーブル作成後は件数を確認・出力する
- [ ] **DP-005**: `saveAsTable()` の前に `.write.format("delta")` を明示する

**例（良い）:**
```python
# 冪等性保証
(df
    .write
    .format("delta")
    .mode("overwrite")  # ✅ mode明示
    .option("delta.enableChangeDataFeed", "true")  # ✅ CDF有効化
    .saveAsTable(CHUNKED_DOCS_TABLE))

# 確認
count = spark.table(CHUNKED_DOCS_TABLE).count()
print(f"✅ {count}件を {CHUNKED_DOCS_TABLE} に保存")
```

**例（悪い）:**
```python
df.write.saveAsTable(TABLE)  # ❌ mode未指定、format未指定
# ❌ 確認なし
```

---

### 📌 Pandas UDF

- [ ] **DP-006**: Pandas UDFには必ず型アノテーションを記述する
- [ ] **DP-007**: UDF内で外部状態に依存しない（純粋関数）
- [ ] **DP-008**: 重い初期化処理はUDF外で行う
- [ ] **DP-009**: UDFの戻り値スキーマは明示的に定義する
- [ ] **DP-010**: エラーハンドリングをUDF内に実装する

**例（良い）:**
```python
# UDF外で初期化（ワーカーで1回のみ）
tokenizer = OpenAIGPTTokenizer.from_pretrained("openai-gpt")
text_splitter = RecursiveCharacterTextSplitter(...)

@pandas_udf("array<string>")  # ✅ スキーマ明示
def chunk_text(texts: pd.Series) -> pd.Series:
    """テキストをチャンクに分割（純粋関数）"""
    def split(text: str) -> List[str]:
        try:
            if not text or len(text.strip()) < MIN_SIZE:
                return []
            return text_splitter.split_text(text)
        except Exception as e:
            print(f"Warning: {e}")
            return []

    return texts.apply(split)
```

**例（悪い）:**
```python
@pandas_udf("array<string>")
def chunk_text(texts):  # ❌ 型ヒントなし
    # ❌ UDF内で重い初期化
    tokenizer = OpenAIGPTTokenizer.from_pretrained("openai-gpt")

    # ❌ エラーハンドリングなし
    return texts.apply(lambda x: text_splitter.split_text(x))
```

---

### 📌 Vector Search操作

- [ ] **DP-011**: Vector Index作成は冪等性を保証する
- [ ] **DP-012**: Index準備完了を待機するロジックを実装する
- [ ] **DP-013**: Delta Sync Indexのパイプラインタイプを明示する
- [ ] **DP-014**: Index作成後はテスト検索を実行する
- [ ] **DP-015**: primary_keyとembedding_source_columnを明示する

**例（良い）:**
```python
# 冪等性保証
try:
    index = vsc.get_index(VECTOR_SEARCH_ENDPOINT, VECTOR_INDEX_NAME)
    index.sync()
    print("⚠️  既存Index同期")
except ResourceNotFoundError:
    vsc.create_delta_sync_index(
        endpoint_name=VECTOR_SEARCH_ENDPOINT,
        index_name=VECTOR_INDEX_NAME,
        source_table_name=CHUNKED_DOCS_TABLE,
        pipeline_type="TRIGGERED",  # ✅ 明示
        primary_key="id",            # ✅ 明示
        embedding_source_column="content"  # ✅ 明示
    )
    print("🆕 新規Index作成")

# 準備待機
wait_for_index_ready(VECTOR_INDEX_NAME, max_wait=600)

# テスト検索
test_search(VECTOR_INDEX_NAME, "テストクエリ")
```

---

## ✅ MLOps規約

### 📌 MLflow操作

- [ ] **ML-001**: Unity Catalog統合を明示的に設定する
- [ ] **ML-002**: モデルシグネチャを必ず定義する
- [ ] **ML-003**: `pip_requirements` を明示的に記述する
- [ ] **ML-004**: `input_example` を提供する
- [ ] **ML-005**: ログ時に `run_name` を設定する
- [ ] **ML-006**: 重要なパラメータ・メトリクスをログする

**例（良い）:**
```python
mlflow.set_registry_uri("databricks-uc")  # ✅ UC統合

# シグネチャ作成
question = {"query": "テスト質問"}
answer = rag_chain.run(question)
signature = infer_signature(question, answer)

with mlflow.start_run(run_name=f"rag_chatbot_{ENV}"):
    # パラメータロギング
    mlflow.log_params({
        "embedding_model": EMBEDDING_MODEL_ENDPOINT,
        "llm_model": LLM_ENDPOINT,
        "chunk_size": CHUNK_CONFIG["max_size"]
    })

    # メトリクスロギング
    mlflow.log_metrics({
        "num_documents": doc_count,
        "num_chunks": chunk_count
    })

    # モデルロギング
    mlflow.langchain.log_model(
        rag_chain,
        artifact_path="chain",
        registered_model_name=MODEL_NAME,
        pip_requirements=[...],  # ✅ 明示
        input_example=question,  # ✅ 提供
        signature=signature      # ✅ 定義
    )
```

**例（悪い）:**
```python
# ❌ UC統合なし
mlflow.langchain.log_model(rag_chain, "chain")
# ❌ シグネチャなし
# ❌ pip_requirementsなし
# ❌ パラメータ・メトリクスログなし
```

---

### 📌 モデルデプロイ

- [ ] **ML-007**: デプロイ前に最新バージョンを取得する
- [ ] **ML-008**: エンドポイント作成は冪等性を保証する
- [ ] **ML-009**: `workload_size` を明示的に設定する
- [ ] **ML-010**: `scale_to_zero_enabled` を設定する
- [ ] **ML-011**: 環境変数でSecretsを参照する
- [ ] **ML-012**: デプロイ後はテストクエリを実行する

**例（良い）:**
```python
# 最新バージョン取得
versions = client.get_latest_versions(MODEL_NAME, stages=["None"])
if not versions:
    raise Exception(f"モデルが見つかりません: {MODEL_NAME}")
latest_version = versions[0].version

# 冪等性保証
existing = next(
    (e for e in w.serving_endpoints.list() if e.name == ENDPOINT_NAME),
    None
)

endpoint_config = EndpointCoreConfigInput(
    served_models=[
        ServedModelInput(
            model_name=MODEL_NAME,
            model_version=latest_version,
            workload_size="Small",              # ✅ 明示
            scale_to_zero_enabled=True,         # ✅ 設定
            environment_vars={                  # ✅ Secrets参照
                "DATABRICKS_TOKEN": f"{{{{secrets/{SECRET_SCOPE}/{SECRET_KEY}}}}}"
            }
        )
    ]
)

if existing:
    w.serving_endpoints.update_config_and_wait(...)
else:
    w.serving_endpoints.create_and_wait(...)

# テストクエリ
test_deployment(ENDPOINT_NAME, test_queries)
```

---

## ✅ セキュリティ規約

### 📌 認証・認可

- [ ] **SC-001**: トークンをハードコードしない
- [ ] **SC-002**: Databricks Secretsを使用する
- [ ] **SC-003**: 環境変数からトークンを読み込む
- [ ] **SC-004**: コードにパスワードやAPIキーを含めない
- [ ] **SC-005**: `.gitignore` にシークレットファイルを追加する

**例（良い）:**
```python
# Databricks Secrets使用
TOKEN = dbutils.secrets.get(SECRET_SCOPE, SECRET_KEY)

# 環境変数使用（ローカル）
import os
TOKEN = os.getenv("DATABRICKS_TOKEN")

# Model Serving環境変数（Secrets参照）
environment_vars={
    "DATABRICKS_TOKEN": f"{{{{secrets/{SECRET_SCOPE}/{SECRET_KEY}}}}}"
}
```

**例（悪い）:**
```python
TOKEN = "dapi1234567890abcdef"  # ❌ ハードコード
PASSWORD = "my_password"         # ❌ パスワード記述
```

---

### 📌 Unity Catalogアクセス制御

- [ ] **SC-006**: テーブルに適切なGRANT権限を設定する
- [ ] **SC-007**: モデルに適切なEXECUTE権限を設定する
- [ ] **SC-008**: 最小権限の原則を適用する
- [ ] **SC-009**: サービスプリンシパルを使用する（本番環境）

**例（良い）:**
```sql
-- テーブル権限
GRANT SELECT ON TABLE rag_demo_prod.chatbot.chunked_documents
  TO `data-scientists`;

-- モデル権限
GRANT EXECUTE ON MODEL rag_demo_prod.chatbot.rag_chatbot
  TO `ml-engineers`;

-- 最小権限
REVOKE ALL PRIVILEGES ON CATALOG rag_demo_prod FROM `public`;
```

---

## ✅ パフォーマンス規約

### 📌 データ処理

- [ ] **PF-001**: 大規模データには分散処理（Spark）を使用する
- [ ] **PF-002**: 不要なデータは早期にフィルタリングする
- [ ] **PF-003**: `collect()` は必要最小限にする
- [ ] **PF-004**: `cache()` を適切に使用する
- [ ] **PF-005**: パーティショニングを考慮する

**例（良い）:**
```python
# 分散処理でチャンク化
chunked_df = (df
    .filter(F.length(F.col("text")) > MIN_SIZE)  # ✅ 早期フィルタ
    .withColumn("chunks", chunk_udf(F.col("text")))
    .cache()  # ✅ 再利用のためキャッシュ
)

# サンプル表示のみcollect
samples = chunked_df.limit(5).collect()  # ✅ limit後にcollect
```

**例（悪い）:**
```python
# ❌ 全データをcollectして処理
all_data = df.collect()
for row in all_data:
    chunks = chunk_text(row['text'])
```

---

### 📌 モデル推論

- [ ] **PF-006**: バッチ推論を使用する（可能な場合）
- [ ] **PF-007**: 適切なタイムアウトを設定する
- [ ] **PF-008**: リトライロジックを実装する
- [ ] **PF-009**: レスポンスキャッシュを検討する
- [ ] **PF-010**: 適切なworkload_sizeを選択する

**例（良い）:**
```python
# タイムアウト設定
response = requests.post(
    endpoint_url,
    json=payload,
    timeout=60  # ✅ タイムアウト
)

# リトライロジック
for attempt in range(MAX_RETRIES):
    try:
        response = call_endpoint()
        break
    except requests.exceptions.Timeout:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_INTERVAL)
        else:
            raise
```

---

## ✅ ドキュメント規約

### 📌 ノートブックドキュメント

- [ ] **DC-001**: ノートブック冒頭に目的を記述する
- [ ] **DC-002**: 各セクションに見出しを付ける
- [ ] **DC-003**: 複雑な処理にはコメントを追加する
- [ ] **DC-004**: 前提条件を明記する
- [ ] **DC-005**: 次のステップを明記する

**例（良い）:**
```python
# Databricks notebook source
# MAGIC %md
# MAGIC # データ取得・チャンク化パイプライン
# MAGIC
# MAGIC ## 目的
# MAGIC ドキュメントを取得し、LLM処理用にチャンク化する
# MAGIC
# MAGIC ## 前提条件
# MAGIC - Unity Catalogが設定済み
# MAGIC - Vector Search Endpointが作成済み
# MAGIC
# MAGIC ## 処理フロー
# MAGIC 1. サンプルドキュメント生成
# MAGIC 2. LangChainでチャンク化
# MAGIC 3. Delta Tableに保存
# MAGIC
# MAGIC ## 次のステップ
# MAGIC `02-create-vector-index.py` を実行してVector Indexを作成

# COMMAND ----------

%run ../00-config

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. データ取得
```

---

### 📌 コメント

- [ ] **DC-006**: `# TODO:` で未実装機能を明記する
- [ ] **DC-007**: `# FIXME:` で修正が必要な箇所を明記する
- [ ] **DC-008**: `# NOTE:` で重要な注意事項を明記する
- [ ] **DC-009**: コメントは「なぜ」を説明する（「何を」ではなく）
- [ ] **DC-010**: 古いコメントアウトコードは削除する

**例（良い）:**
```python
# NOTE: トークンベースでチャンク化（文字数ベースではない理由：LLMのコンテキスト制限）
text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(...)

# TODO: 本番環境ではS3からドキュメントを読み込む
sample_docs = [...]

# FIXME: エラーハンドリングを強化（issue #123）
try:
    result = process()
except:
    pass
```

**例（悪い）:**
```python
# データを取得  # ❌ 「何を」のみ説明
df = get_data()

# # old_function()  # ❌ コメントアウトコード残存
# # legacy_code = True
```

---

## ✅ テスト規約

### 📌 テストケース

- [ ] **TS-001**: 各ノートブックに動作確認テストを含める
- [ ] **TS-002**: 正常系と異常系の両方をテストする
- [ ] **TS-003**: テスト結果を明示的に出力する
- [ ] **TS-004**: 期待値と実際の値を比較する
- [ ] **TS-005**: エッジケースをテストする

**例（良い）:**
```python
# COMMAND ----------
# MAGIC %md
# MAGIC ## テスト

# COMMAND ----------

test_cases = [
    {
        "query": "Databricksとは？",
        "expected_keywords": ["Databricks", "データ"]
    },
    {
        "query": "",  # エッジケース
        "expected_keywords": []
    }
]

print("🧪 テスト実行中...")
passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['query']}")

    try:
        answer = rag_chain.run({"query": test["query"]})
        found = [kw for kw in test["expected_keywords"] if kw in answer]

        if found or not test["expected_keywords"]:
            print(f"✅ PASS")
            passed += 1
        else:
            print(f"❌ FAIL (期待: {test['expected_keywords']})")
            failed += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        failed += 1

print(f"\n結果: {passed}/{len(test_cases)} passed")

# テスト失敗時は実行を停止
assert failed == 0, f"{failed}件のテストが失敗しました"
```

---

### 📌 統合テスト

- [ ] **TS-006**: デプロイ後はエンドツーエンドテストを実行する
- [ ] **TS-007**: 本番環境デプロイ前にステージング環境でテストする
- [ ] **TS-008**: パフォーマンステスト（レイテンシ計測）を実施する
- [ ] **TS-009**: テストデータは本番データと分離する
- [ ] **TS-010**: テスト結果をログに記録する

**例（良い）:**
```python
# デプロイメントテスト
print("🧪 デプロイメントテスト実行中...")

test_queries = ["質問1", "質問2", "質問3"]
results = []

for q in test_queries:
    start_time = time.time()

    try:
        response = w.serving_endpoints.query(
            SERVING_ENDPOINT_NAME,
            dataframe_records=[{"query": q}]
        )
        latency = time.time() - start_time

        assert response.predictions[0], "空のレスポンス"

        print(f"✅ 成功 (レイテンシ: {latency:.2f}秒)")
        results.append({"query": q, "status": "success", "latency": latency})

    except Exception as e:
        print(f"❌ 失敗: {e}")
        results.append({"query": q, "status": "failed", "error": str(e)})

# 成功率確認
success_rate = sum(1 for r in results if r["status"] == "success") / len(results)
assert success_rate >= 0.9, f"テスト成功率が低い: {success_rate:.1%}"

print(f"\n✅ テスト成功率: {success_rate:.1%}")
```

---

## 📊 チェックリスト使用方法

### レビュー時の手順

1. **該当カテゴリを選択**: 変更内容に応じてチェック項目を選択
2. **各項目を確認**: チェックボックスをマークダウンで確認
3. **問題箇所を記録**: 違反項目をコメントに記載
4. **修正依頼**: プルリクエストで修正を依頼

### 優先度

| 優先度 | カテゴリID | 説明 |
|-------|-----------|------|
| **Critical** | SC-xxx, DP-001~005 | セキュリティ、データ整合性 |
| **High** | NB-xxx, ML-xxx | Databricks規約、MLOps |
| **Medium** | CD-xxx, PF-xxx | コード品質、パフォーマンス |
| **Low** | DC-xxx | ドキュメント |

### レビューコメント例

```markdown
## コードレビュー

### Critical Issues
- [ ] **SC-001**: L42でトークンがハードコードされています
- [ ] **DP-002**: L78でDelta Tableのmodeが指定されていません

### High Issues
- [ ] **NB-004**: L15で`%pip install`後に`restartPython()`がありません
- [ ] **ML-002**: L120でモデルシグネチャが定義されていません

### Medium Issues
- [ ] **CD-006**: L55の関数に型ヒントがありません
- [ ] **PF-003**: L92で全データを`collect()`しています

### Suggestions
- **DC-001**: ノートブック冒頭に目的を記述することを推奨します
```

---

## 🔧 トラブルシューティング

### よくあるエラーと解決方法

#### ImportError: No module named 'databricks.vector_search.client'

**原因**: `databricks-vectorsearch`パッケージがインストールされていない

**解決方法**:
```python
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
```

**関連チェック項目**: NB-008, NB-009, NB-011, NB-012

---

#### ModuleNotFoundError: No module named 'langchain'

**原因**: LangChain関連パッケージがインストールされていない

**解決方法**:
```python
%pip install langchain langchain-community --quiet
dbutils.library.restartPython()
```

**関連チェック項目**: NB-008, NB-009

---

#### NameError: name 'CATALOG' is not defined

**原因**: `00-config.py`が読み込まれていない、または`restartPython()`後に再読み込みされていない

**解決方法**:
```python
# restartPython()の後に必ず%runを実行
dbutils.library.restartPython()

# COMMAND ----------

%run ../00-config
```

**関連チェック項目**: NB-003, NB-012

---

#### AnalysisException: Catalog 'rag_demo_dev' not found

**原因**: Unity Catalogが作成されていない、または権限がない

**解決方法**:
```python
# 01-setup/01-validate-environment.py を実行
# または手動でCatalogを作成
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
```

**関連チェック項目**: CF-001, SC-006

---

## 🔄 チェックリスト更新

このチェックリストは以下のタイミングで更新します：

- 新しいベストプラクティスが確立された時
- Databricksプラットフォームの更新時
- プロジェクト固有の規約が追加された時
- レビューで頻繁に指摘される項目が発見された時

**最終更新日**: 2026-01-07
**バージョン**: 1.1
**管理者**: ML Engineering Team

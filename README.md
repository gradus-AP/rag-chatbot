# Databricks RAG Chatbot

Databricksプラットフォーム上で動作する、Retrieval-Augmented Generation (RAG) ベースのエンタープライズグレードチャットボットシステム

[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=flat&logo=databricks&logoColor=white)](https://databricks.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-green)](https://langchain.com/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat&logo=mlflow&logoColor=white)](https://mlflow.org/)

---

## 📋 目次

- [概要](#概要)
- [主要機能](#主要機能)
- [プロジェクト構成](#プロジェクト構成)
- [クイックスタート](#クイックスタート)
- [詳細ドキュメント](#詳細ドキュメント)
- [技術スタック](#技術スタック)
- [ライセンス](#ライセンス)

---

## 🎯 概要

このプロジェクトは、Databricksのマネージドサービスを活用した、本番環境対応のRAGチャットボットシステムです。

### 主な特徴

- ✅ **マネージドインフラ**: Databricks Vector Search、Model Servingを活用
- ✅ **データガバナンス**: Unity Catalogによる細粒度アクセス制御
- ✅ **スケーラビリティ**: 自動スケーリング対応（Scale to Zero）
- ✅ **冪等性保証**: 全パイプラインが再実行可能
- ✅ **環境分離**: dev/staging/prod環境の完全分離
- ✅ **エンタープライズ対応**: シークレット管理、監査ログ、リネージ追跡

---

## 🚀 主要機能

### 1. データパイプライン
- ドキュメントの自動取り込み
- LangChainによるインテリジェントなチャンク化
- Delta Lakeへの保存（Change Data Feed有効）
- Vector Search Indexの自動同期

### 2. RAGチェーン
- ベクトル検索ベースのコンテキスト取得
- カスタマイズ可能なプロンプトテンプレート
- DBRX Instructによる高品質な応答生成
- MLflowによるモデルバージョン管理

### 3. モデルサービング
- Databricks Model Servingエンドポイント
- 自動スケーリング（負荷に応じた調整）
- Secretsベースのセキュアな認証
- デプロイメントの自動テスト

### 4. Streamlit UI
- 対話型チャットインターフェース
- Databricks/ローカル環境自動検出
- セッション管理とチャット履歴
- サンプル質問機能

---

## 📁 プロジェクト構成

```
databricks-rag-chatbot/
│
├── 📄 00-config.py                        # 中央設定ファイル
│
├── 📂 01-setup/                          # 環境セットアップ
│   └── 01-validate-environment.py        # 環境検証・初期化
│
├── 📂 02-data-pipeline/                  # データパイプライン
│   ├── 01-ingest-and-chunk.py           # データ取得・チャンク化
│   └── 02-create-vector-index.py        # Vector Index作成
│
├── 📂 03-model/                          # モデル開発・デプロイ
│   ├── 01-build-rag-chain.py            # RAGチェーン構築
│   ├── 02-test-and-register.py          # テスト・MLflow登録
│   └── 03-deploy.py                     # モデルデプロイ
│
├── 📂 04-app/                            # アプリケーション
│   └── streamlit_app.py                 # Streamlit UI
│
├── 📖 DESIGN.md                          # 設計資料（詳細）
├── 📋 CODE_REVIEW_CHECKLIST.md          # コードレビューチェックリスト
└── 📘 README.md                          # このファイル
```

---

## ⚡ クイックスタート

### 前提条件

- Databricksワークスペース（Premium以上推奨）
- Unity Catalogが有効化されていること
- Vector Search Endpointが作成済み

### セットアップ手順

#### Step 1: 設定ファイルの編集

```python
# 00-config.py を開き、以下を編集
ENV = "dev"  # 環境を選択（dev/staging/prod）
CATALOG = "your_catalog_name"
VECTOR_SEARCH_ENDPOINT = "your_vs_endpoint"
```

#### Step 2: 環境検証

```bash
# Databricksノートブックで実行
01-setup/01-validate-environment.py
```

**期待される出力:**
```
✅ Catalog: your_catalog_name
✅ Schema: chatbot
✅ Vector Endpoint: your_vs_endpoint
✅ Secrets: rag_demo_dev/api_token
🎉 すべての検証に成功！
```

#### Step 3: データパイプライン実行

```bash
# データ取得・チャンク化
02-data-pipeline/01-ingest-and-chunk.py

# Vector Index作成
02-data-pipeline/02-create-vector-index.py
```

**期待される出力:**
```
✅ 5件を rag_demo_dev.chatbot.raw_documents に保存
✅ 150チャンクを rag_demo_dev.chatbot.chunked_documents に保存
✅ Index準備完了！
```

#### Step 4: モデル開発・デプロイ

```bash
# RAGチェーン構築
03-model/01-build-rag-chain.py

# テスト・MLflow登録
03-model/02-test-and-register.py

# モデルデプロイ
03-model/03-deploy.py
```

**期待される出力:**
```
✅ RAGチェーン構築完了
結果: 3/3 passed
✅ モデル登録完了: rag_demo_dev.chatbot.rag_chatbot
✅ エンドポイント作成完了！
```

#### Step 5: Streamlit UI起動

```bash
# Databricks環境内
04-app/streamlit_app.py

# ローカル環境
export DATABRICKS_TOKEN="your_token"
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
streamlit run 04-app/streamlit_app.py
```

---

## 📚 詳細ドキュメント

### 設計資料

詳細なアーキテクチャ、データフロー、コンポーネント設計については以下を参照してください：

📖 **[DESIGN.md](DESIGN.md)**

**主な内容:**
- システムアーキテクチャ図
- データフロー詳細
- コンポーネント設計
- セキュリティ設計
- 運用設計
- スケーリング戦略

### コードレビューガイドライン

コードレビュー時のチェックリストは以下を参照してください：

📋 **[CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md)**

**主な内容:**
- Databricksノートブック規約（90項目）
- コーディング規約
- データパイプライン規約
- MLOps規約
- セキュリティ規約
- テスト規約

---

## 🛠️ 技術スタック

### コアテクノロジー

| カテゴリ | 技術 | 用途 |
|---------|------|------|
| **プラットフォーム** | Databricks | 統合データプラットフォーム |
| **ストレージ** | Delta Lake | ACIDトランザクション、タイムトラベル |
| **ガバナンス** | Unity Catalog | データガバナンス、アクセス制御 |
| **ベクトル検索** | Databricks Vector Search | マネージド類似検索 |
| **LLM** | DBRX Instruct | 自然言語生成 |
| **埋め込み** | text-embedding-ada-002 | テキストベクトル化 |
| **オーケストレーション** | LangChain | RAGパイプライン構築 |
| **モデル管理** | MLflow | 実験追跡、モデル登録 |
| **UI** | Streamlit | Webアプリケーション |

### Python依存関係

```txt
langchain>=0.1.0
langchain-community>=0.1.0
databricks-vectorsearch>=0.22
mlflow>=2.9.0
transformers>=4.30.0
streamlit>=1.30.0
requests>=2.31.0
pandas>=2.0.0
pyspark>=3.5.0
```

---

## 🔒 セキュリティ

### 認証・認可

- **Databricks Secrets**: トークン、APIキーの安全な管理
- **Unity Catalog**: テーブル・モデルレベルのアクセス制御
- **Bearer認証**: Model Servingエンドポイントへのセキュアなアクセス

### ベストプラクティス

```python
# ✅ 正しい - Secretsを使用
TOKEN = dbutils.secrets.get(SECRET_SCOPE, SECRET_KEY)

# ❌ 悪い - ハードコード
TOKEN = "dapi1234567890"
```

---

## 📊 運用

### モニタリング

- **Model Serving Dashboard**: リクエスト数、レイテンシ、エラー率
- **MLflow Tracking**: 実験メトリクス、パラメータ
- **Unity Catalog監査ログ**: アクセスログ、データリネージ

### スケーリング

```python
# 自動スケーリング設定
workload_size="Small"           # 低負荷
scale_to_zero_enabled=True      # コスト最適化
```

### バックアップ・リカバリ

```python
# Delta Lakeタイムトラベル
df = spark.read.format("delta").option("versionAsOf", 3).table(TABLE_NAME)

# モデルバージョン管理
client.transition_model_version_stage(name=MODEL_NAME, version="2", stage="Production")
```

---

## 🎯 使用例

### Streamlit UIでの対話

```
ユーザー: Databricksとは？

チャットボット: Databricksは、データレイクハウスプラットフォームで、
Apache Sparkをベースにしています。データエンジニアリング、
機械学習、分析を統合的に行うことができます。
```

### Python APIでの呼び出し

```python
import requests

url = "https://your-workspace.cloud.databricks.com/serving-endpoints/rag_endpoint_dev/invocations"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
data = {"dataframe_records": [{"query": "Databricksとは？"}]}

response = requests.post(url, headers=headers, json=data)
print(response.json()["predictions"][0])
```

---

## 🔄 環境切り替え

### Dev → Staging → Prod

```python
# 00-config.py
ENV = "dev"      # 開発環境
ENV = "staging"  # ステージング環境
ENV = "prod"     # 本番環境
```

環境ごとに独立したリソースが作成されます：
- Catalog: `rag_demo_{env}`
- Endpoint: `rag_endpoint_{env}`
- Secrets: `rag_demo_{env}`

---

## 🤝 コントリビューション

### プルリクエスト手順

1. フィーチャーブランチを作成
2. [CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md) でセルフチェック
3. テストを実行（`02-test-and-register.py`）
4. プルリクエストを作成

### コーディング規約

詳細は [CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md) を参照してください。

**重要な規約:**
- Databricks MAGICコマンドの正しい使用
- 型ヒントの記述
- 冪等性の保証
- エラーハンドリング
- セキュリティベストプラクティス

---

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

## 📧 サポート

質問や問題がある場合は、以下にお問い合わせください：

- **Issues**: [GitHub Issues](https://github.com/your-org/databricks-rag-chatbot/issues)
- **Email**: ml-engineering@your-org.com
- **Slack**: #databricks-rag-support

---

## 🎓 参考資料

- [Databricks Vector Search Documentation](https://docs.databricks.com/en/generative-ai/vector-search.html)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Unity Catalog Best Practices](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)

---

**Version**: 1.0
**Last Updated**: 2026-01-07
**Maintained by**: ML Engineering Team
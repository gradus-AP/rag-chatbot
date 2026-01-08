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
**最終更新:** 2026-01-07

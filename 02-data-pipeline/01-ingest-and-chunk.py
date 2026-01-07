# Databricks notebook source
# ========================================
# データ取得 + チャンク化（統合版）
# ========================================

# COMMAND ----------

%pip install transformers langchain>=0.3.0 langchain-core>=0.3.0 langchain-community lxml beautifulsoup4 requests --quiet
dbutils.library.restartPython()

# COMMAND ----------

%run ../00-config

# COMMAND ----------

# データ取得
print("📥 データ取得中...")

sample_docs = [
    {"url": f"https://example.com/doc{i}", "text": f"サンプル文書{i}の内容です。Databricksはデータレイクハウスプラットフォームで、Apache Sparkをベースにしています。" * 30}
    for i in range(1, 6)
]

raw_df = spark.createDataFrame(sample_docs)

# 冪等性: 既存テーブルを上書き
raw_df.write.mode("overwrite").saveAsTable(RAW_DOCS_TABLE)
print(f"✅ {raw_df.count()}件を {RAW_DOCS_TABLE} に保存")

# COMMAND ----------

# チャンク化
print("\n✂️  チャンク化中...")

from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import OpenAIGPTTokenizer
import pyspark.sql.functions as F
from pyspark.sql.functions import pandas_udf
import pandas as pd

tokenizer = OpenAIGPTTokenizer.from_pretrained("openai-gpt")
text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer,
    chunk_size=CHUNK_CONFIG["max_size"],
    chunk_overlap=CHUNK_CONFIG["overlap"]
)

@pandas_udf("array<string>")
def chunk_text(texts: pd.Series) -> pd.Series:
    def split(text):
        if not text or len(text.strip()) < CHUNK_CONFIG["min_size"]:
            return []
        chunks = text_splitter.split_text(text)
        return [c for c in chunks if len(tokenizer.encode(c)) >= CHUNK_CONFIG["min_size"]]
    return texts.apply(split)

# COMMAND ----------

# チャンク化実行
df = spark.table(RAW_DOCS_TABLE)

chunked_df = (df
    .withColumn("chunks", chunk_text(F.col("text")))
    .withColumn("content", F.explode(F.col("chunks")))
    .withColumn("id", F.monotonically_increasing_id())
    .select("id", "url", "content")
)

# Change Data Feed有効化
(chunked_df
    .write
    .mode("overwrite")
    .option("delta.enableChangeDataFeed", "true")
    .saveAsTable(CHUNKED_DOCS_TABLE))

print(f"✅ {chunked_df.count()}チャンクを {CHUNKED_DOCS_TABLE} に保存")

# COMMAND ----------

# 結果確認
display(spark.table(CHUNKED_DOCS_TABLE).limit(5))

# COMMAND ----------

# サンプル表示
print("\n📊 チャンクサンプル:")
for row in spark.table(CHUNKED_DOCS_TABLE).limit(3).collect():
    print(f"\nID: {row['id']}")
    print(f"URL: {row['url']}")
    print(f"Content: {row['content'][:100]}...")
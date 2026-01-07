import streamlit as st
import requests
import os

# Databricks環境検出
try:
    from dbruntime.databricks_repl_context import get_context
    ctx = get_context()
    TOKEN = ctx.apiToken
    WORKSPACE_URL = ctx.apiUrl
    IN_DATABRICKS = True
except:
    TOKEN = os.getenv("DATABRICKS_TOKEN")
    WORKSPACE_URL = os.getenv("DATABRICKS_HOST")
    IN_DATABRICKS = False

# 設定（ENVに応じて変更）
ENV = "dev"
ENDPOINT_NAME = f"rag_endpoint_{ENV}"
ENDPOINT_URL = f"{WORKSPACE_URL}/serving-endpoints/{ENDPOINT_NAME}/invocations"

# ページ設定
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ヘッダー
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🤖 RAG Chatbot")
    st.caption(f"Powered by Databricks DBRX Instruct [{ENV.upper()} 環境]")
with col2:
    if IN_DATABRICKS:
        st.success("Databricks ✅")
    else:
        st.info("Local 💻")

# チャット履歴初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# チャット履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("質問を入力してください"):
    # ユーザーメッセージ追加・表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # API呼び出し
    with st.chat_message("assistant"):
        with st.spinner("🤔 考え中..."):
            try:
                response = requests.post(
                    ENDPOINT_URL,
                    headers={
                        "Authorization": f"Bearer {TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "dataframe_records": [{"query": prompt}]
                    },
                    timeout=60
                )
                response.raise_for_status()
                answer = response.json()["predictions"][0]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except requests.exceptions.RequestException as e:
                error_msg = f"❌ APIエラー: {str(e)}"
                st.error(error_msg)
                if hasattr(e, 'response') and e.response is not None:
                    st.code(e.response.text)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"❌ エラー: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# サイドバー
with st.sidebar:
    st.header("ℹ️ システム情報")
    st.write(f"**エンドポイント:** `{ENDPOINT_NAME}`")
    st.write(f"**環境:** `{ENV}`")
    st.write(f"**実行場所:** {'Databricks' if IN_DATABRICKS else 'Local'}")
    
    st.divider()
    
    st.header("🎯 サンプル質問")
    sample_questions = [
        "Databricksとは？",
        "Sparkの特徴は？",
        "文書の内容を教えて"
    ]
    
    for q in sample_questions:
        if st.button(q, key=f"sample_{q}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    
    st.divider()
    
    # 統計情報
    st.header("📊 チャット統計")
    total_messages = len(st.session_state.messages)
    user_messages = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.metric("総メッセージ数", total_messages)
    st.metric("質問数", user_messages)
    
    st.divider()
    
    # リセットボタン
    if st.button("🗑️ 履歴をクリア", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# フッター
st.divider()
st.caption("💡 ヒント: エンドポイントが応答しない場合は、03-model/03-deploy を確認してください")
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatZhipuAI

load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")

# 1. 初始化組件
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma(persist_directory="./my_chroma_db", embedding_function=embeddings)
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# 🌟 建立對話記憶列表
chat_history = [] 

print("🤖 您的 AI 助手已上線！輸入 'exit' 或 'quit' 結束對話。")

while True:
    user_input = input("\n🙋‍♂️ 你：")
    if user_input.lower() in ["exit", "quit"]:
        break

    # ==========================================
    # 步驟 1：【對話改寫】將追問轉化為獨立問題
    # ==========================================
    standalone_query = user_input
    
    if len(chat_history) > 0:
        # 將歷史對話轉成文字
        history_str = "\n".join([f"User: {q}\nAI: {a}" for q, a in chat_history])
        
        rewrite_prompt = f"""請根據以下的對話歷史，將使用者的「最新提問」改寫成一個「獨立且完整的問題」。
即使問題中包含「它」、「他」或「這件事」，也要改寫成具體的名詞。

【對話歷史】
{history_str}

【最新提問】
{user_input}

獨立問題："""
        
        # 讓 AI 幫我們改寫問題
        standalone_query = llm.invoke(rewrite_prompt).content
        print(f"🔍 (內部改寫問題為：{standalone_query})")

    # ==========================================
    # 步驟 2：【精準檢索】使用改寫後的完整問題
    # ==========================================
    results = vectorstore.similarity_search(standalone_query, k=3)
    context_text = "\n".join([doc.page_content for doc in results])

    # ==========================================
    # 步驟 3：【生成回答】帶入歷史與檢索資料
    # ==========================================
    final_prompt = f"""你是一個專業的助理。請根據以下「參考資料」回答問題。
    
【參考資料】
{context_text}

【問題】
{standalone_query}

回答："""

    response = llm.invoke(final_prompt).content
    
    print(f"\n🤖 AI：{response}")

    # ==========================================
    # 步驟 4：【更新記憶】把這次對話存入歷史
    # ==========================================
    chat_history.append((user_input, response))
    
    # 為了防止記憶太長，我們只保留最近 5 輪對話
    if len(chat_history) > 5:
        chat_history.pop(0)
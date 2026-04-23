import os
from dotenv import load_dotenv
# 🌟 這次我們不匯入對話模型，而是匯入「向量化模型」
# 把 ZhipuAIEmbeddings 換成這個：
# 把 ZhipuAIEmbeddings 換成這個：
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

print("⏳ 正在下載並啟動開源本地向量化引擎 (第一次執行會稍微久一點下載模型)...")
# 初始化本地開源模型 (完全免費！)
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

# ... (後面的 word1, word2, vec1 等等所有代碼，完全不需要動！) ...

# 2. 準備你的測試詞彙
word1 = input("請輸入第一個詞彙 (例如：蘋果)：")
word2 = input("請輸入第二個詞彙 (例如：水果)：")
word3 = input("請輸入第三個詞彙 (例如：太陽)：")

print("\n🧠 正在將文字轉換成數字(向量)...")
# embed_query 就是施展魔法的咒語，它會把文字送給 AI，換回一串數字
vec1 = embeddings.embed_query(word1)
vec2 = embeddings.embed_query(word2)
vec3 = embeddings.embed_query(word3)

# 讓我們偷看一下這個「數字(座標)」到底長什麼樣子
print("✅ 轉換成功！")
print(f"「{word1}」被轉成了一個長度為 {len(vec1)} 的數字陣列！")
print(f"偷看前 5 個維度的數字：{vec1[:5]}")

# ==========================================
# 3. 數學黑魔法：計算相似度 (餘弦相似度 Cosine Similarity)
# ⚠️ 備註：這段數學函數你不用背，以後 LangChain 會幫我們自動算好！
# ==========================================
def calculate_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = sum(a * a for a in v1) ** 0.5
    norm_b = sum(b * b for b in v2) ** 0.5
    return dot_product / (norm_a * norm_b)

# 4. 進行對決！
sim_apple_fruit = calculate_similarity(vec1, vec2)
sim_apple_car = calculate_similarity(vec1, vec3)

print("\n🔍 語意相似度大對決 (範圍 -1 到 1，越接近 1 越相似)：")
print(f"🍏「{word1}」 vs 🍎「{word2}」 -> 相似度分數：{sim_apple_fruit:.4f}")
print(f"🍏「{word1}」 vs 🚗「{word3}」 -> 相似度分數：{sim_apple_car:.4f}")
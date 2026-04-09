import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 1. 載入金鑰並初始化客戶端
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
client = ZhipuAI(api_key=api_key)

# ==========================================
# 步驟一：專職「總結」的 AI 函數
# ==========================================
def step1_summarize(text):
    print("正在進行第一步：總結文章...")
    response = client.chat.completions.create(
        model="glm-4-flashx",
        messages=[
            {
                "role": "system",
                "content": "你是一個精準的摘要助手。請用「一句話」總結使用者提供的文章核心內容。不要輸出多餘的廢話。"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return response.choices[0].message.content.strip()

# ==========================================
# 步驟二：專職「翻譯」的 AI 函數
# ==========================================
def step2_translate(text, target_language="英文"):
    print(f"正在進行第二步：將摘要翻譯成 {target_language}...")
    response = client.chat.completions.create(
        model="glm-4-flashx",
        messages=[
            {
                "role": "system",
                "content": f"你是一個專業翻譯。請將使用者的文字翻譯成{target_language}。只輸出翻譯結果，絕對不要有任何解釋。"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return response.choices[0].message.content.strip()

# ==========================================
# 主管函數：將兩個步驟串接成「流水線」 (Chaining)
# ==========================================
def process_pipeline(article):
    print("开始流水线处理...")

    summary = step1_summarize(article)
    print("第一步结果（摘要）:", summary)
    translation = step2_translate(summary)
    print("第二步结果（翻译）:", translation)
    print("流水线处理完成！")

if __name__ == "__main__":
    # 我們模擬一篇落落長的科技文章
    long_article = """
    蘋果公司（Apple）今日無預警在官網上架了搭載全新 M4 晶片的 iPad Pro。
    這款新設備不僅是有史以來最薄的蘋果產品，還首次採用了雙層 OLED 面板技術，
    帶來了極致的亮度和對比度。此外，配合全新的巧控鍵盤和 Apple Pencil Pro，
    蘋果進一步模糊了平板電腦與傳統筆記型電腦之間的界線。雖然起售價有所上漲，
    但市場分析師普遍認為，憑藉其強大的 AI 運算能力，這款產品將在專業創作者市場引起熱烈迴響。
    """

    print("原始長篇文章：")
    print(long_article)

    # 啟動流水線
    process_pipeline(long_article)
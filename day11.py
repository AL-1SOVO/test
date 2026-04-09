import os
import json
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
client = ZhipuAI(api_key=api_key)

def analyze_news(news_text):
    system_prompt = """
    你是一個專業的資料提取 API 伺服器。
    請閱讀使用者提供的新聞，並嚴格按照以下 JSON 格式輸出分析結果。
    
    【規則】
    1. 不要輸出任何解釋性文字（例如"好的"、"這是我分析的結果"）。
    2. 不要使用 Markdown 語法包裝（不要加上 ```json 標籤）。
    3. 必須是合法的 JSON 格式。

    【輸出格式】
    {
        "title": "你為新聞總結的一句話標題",
        "keywords": ["關鍵字1", "關鍵字2", "關鍵字3"],
        "sentiment": "正面/負面/中立"
    }
    """

    try:
        print("正在分析新聞并转化为json...")
        response = client.chat.completions.create(
            model="glm-4-flashx",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": news_text}
            ],
            temperature=0.2
        )

        raw_result = response.choices[0].message.content.strip()

        print("原始结果:", raw_result)
        cleaned_result = raw_result.strip()
        if cleaned_result.startswith('```json'):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.endswith('```'):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()
        cleaned_result = cleaned_result.strip()

        parsed_json = json.loads(cleaned_result)
        return parsed_json
    
    except json.JSONDecodeError as e:
        print("JSON解析错误:", e)
        print(f"AI 實際回傳內容：\n{raw_result}")
        return None
    except Exception as e:
        print("分析過程中發生錯誤:", e)
        return None
    
if __name__ == "__main__":
    # 我們模擬一篇新聞報導
    sample_news = "今日科技巨頭發布了最新的AI晶片，性能提升了三倍，同時功耗降低了50%。市場對此反應熱烈，股價開盤大漲8%。然而，部分專家擔憂這將加劇全球晶片供應鏈的競爭壓力。"

    print(f"📰 新聞內容：\n{sample_news}\n")
    
    # 執行分析
    result = analyze_news(sample_news)

    if result:
        print("✅ 成功獲得結構化數據！(現在它是可以被 Python 調用的資料了)")
        print("-" * 30)
        # 現在你可以像操作一般 Python 字典一樣，精準提取你想要的欄位
        print(f"📌 標題：{result['title']}")
        print(f"🔑 關鍵字：{', '.join(result['keywords'])}")
        print(f"🎭 情感傾向：{result['sentiment']}")
        print("-" * 30)
        print("\n[底層視角] 真正的 Python 字典長這樣：", type(result))
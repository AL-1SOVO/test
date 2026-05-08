import json

# ==========================================
# 🌟 定义工具的“说明书” (JSON Schema 格式)
# ==========================================
# 这就是一个标准的 OpenAI/智谱 等大模型都能看懂的工具描述字典
get_sensor_data_schema = {
    "type": "function", # 声明这是一个函数工具
    "function": {
        "name": "get_sensor_data", # 🔴 必须是纯英文，大模型在决定调用时会输出这个名字
        "description": "获取指定位置和类型的物联网传感器实时数据。", # 🔴 最重要的一环！大模型靠这段中文描述来判断什么时候该用这个工具
        "parameters": {
            "type": "object",
            "properties": {
                # 参数 1：位置
                "location": {
                    "type": "string",
                    "description": "传感器的所在位置，例如：'一号车间', '办公楼屋顶', '仓库A区'"
                },
                # 参数 2：传感器类型
                "sensor_type": {
                    "type": "string",
                    "enum": ["temperature", "humidity", "pressure"], # enum 代表枚举，告诉 AI 只能从这三个词里选一个
                    "description": "需要获取的传感器数据类型。只能是温度(temperature)、湿度(humidity)或压力(pressure)。"
                }
            },
            # 声明哪些参数是必须提供的
            "required": ["location", "sensor_type"]
        }
    }
}

# ==========================================
# 🖨️ 打印出来看看
# ==========================================
print("🛠️ 工具说明书 (JSON Schema) 定义完成！\n")
# json.dumps 用来把 Python 字典漂亮地打印成 JSON 字符串格式
print(json.dumps(get_sensor_data_schema, indent=4, ensure_ascii=False))
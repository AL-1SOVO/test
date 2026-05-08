import random
import time

# ==========================================
# 🛠️ 工具 1：获取传感器数据
# ==========================================
def get_sensor_data(sensor_type: str) -> str:
    """
    模拟从农业物联网网关获取传感器实时数据。
    """
    print(f"📡 [硬件日志] 正在建立与 '{sensor_type}' 传感器的连接...")
    time.sleep(1) # 模拟网络请求的延迟
    
    # 根据传入的传感器类型，返回不同的模拟数据
    if sensor_type == "leaf_temperature":
        # 模拟叶片温度 (20.0°C ~ 35.0°C)
        value = round(random.uniform(20.0, 35.0), 1)
        result = f"{value}°C"
        
    elif sensor_type == "fruit_diameter":
        # 模拟果实直径 (30.0mm ~ 80.0mm)
        value = round(random.uniform(30.0, 80.0), 1)
        result = f"{value}mm"
        
    elif sensor_type == "soil_moisture":
        # 模拟土壤湿度 (20% ~ 80%)
        value = round(random.uniform(20.0, 80.0), 1)
        result = f"{value}%"
        
    else:
        result = f"错误：未知的传感器类型 '{sensor_type}'"
        
    print(f"✅ [硬件日志] 获取成功！数据为: {result}")
    return result

# ==========================================
# 🛠️ 工具 2：控制水肥一体化设备
# ==========================================
def activate_water_fertilizer(duration: int) -> str:
    """
    模拟向底层单片机发送指令，开启水肥一体化设备。
    """
    print(f"💧 [硬件日志] 指令下发：开启水肥一体化阀门...")
    time.sleep(0.5) # 模拟硬件响应
    
    print(f"⏳ [硬件日志] 设备运行中... 设定时长：{duration} 分钟。")
    # 为了测试方便，我们不真的等那么久，只模拟等待1秒钟
    time.sleep(1) 
    
    print("🔒 [硬件日志] 阀门已自动关闭。")
    
    # 必须给 AI 返回一个明确的字符串结果，告诉它任务到底有没有成功
    return f"操作成功：水肥一体化设备已完成 {duration} 分钟的灌溉作业。"

# ==========================================
# 🏃‍♂️ 本地测试区 (不连接 AI，直接用纯 Python 跑跑看)
# ==========================================
if __name__ == "__main__":
    print("=== 🌟 开始本地工具测试 ===\n")
    
    print("👉 测试 1：查询土壤湿度")
    data_1 = get_sensor_data("soil_moisture")
    print(f"最终返回给系统的值: {data_1}\n")
    print("-" * 40)
    
    print("👉 测试 2：启动灌溉设备")
    data_2 = activate_water_fertilizer(15)
    print(f"最终返回给系统的值: {data_2}\n")
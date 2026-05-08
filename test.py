from weasyprint import HTML
import base64

# SVG Icons defined as inline strings to avoid external dependencies
icons = {
    "user": '<svg viewBox="0 0 24 24" width="14" height="14" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
    "gender": '<svg viewBox="0 0 24 24" width="14" height="14" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7z"></path></svg>',
    "phone": '<svg viewBox="0 0 24 24" width="14" height="14" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>',
    "mail": '<svg viewBox="0 0 24 24" width="14" height="14" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>',
    "edu": '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c3 3 9 3 12 0v-5"></path></svg>',
    "work": '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
    "project": '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
    "award": '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"></path></svg>',
    "book": '<svg viewBox="0 0 24 24" width="18" height="18" stroke="#1E3A8A" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>'
}

html_content = f"""
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 12mm 15mm;
            background-color: #ffffff;
        }}
        body {{
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            color: #334155;
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }}
        .header {{
            position: relative;
            margin-bottom: 25px;
            padding-bottom: 10px;
        }}
        .name {{
            font-size: 24pt;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 8px;
        }}
        .info-bar {{
            display: block;
            font-size: 10pt;
            color: #64748b;
        }}
        .info-item {{
            display: inline-block;
            margin-right: 15px;
            vertical-align: middle;
        }}
        .info-item svg {{
            margin-right: 4px;
            vertical-align: -2px;
        }}
        .photo-placeholder {{
            position: absolute;
            top: 0;
            right: 0;
            width: 85px;
            height: 110px;
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            font-size: 9pt;
            text-align: center;
            border-radius: 4px;
        }}
        .section-title {{
            display: flex;
            align-items: center;
            font-size: 14pt;
            font-weight: bold;
            color: #1E3A8A;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .section-title svg {{
            margin-right: 8px;
        }}
        .card {{
            background-color: #F8FAFC;
            padding: 12px 15px;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        .row-header {{
            display: table;
            width: 100%;
            margin-bottom: 6px;
        }}
        .col-left {{ display: table-cell; width: 33.3%; font-weight: bold; color: #000; text-align: left; }}
        .col-mid {{ display: table-cell; width: 33.3%; font-weight: bold; color: #000; text-align: center; }}
        .col-right {{ display: table-cell; width: 33.3%; color: #64748b; text-align: right; font-size: 9pt; }}
        
        .role-title {{ color: #000; font-weight: bold; margin-bottom: 4px; }}
        .description {{ font-size: 10pt; text-align: justify; margin: 0; }}
        .course-list {{ font-size: 9.5pt; margin-top: 5px; }}
        ul {{ margin: 0; padding-left: 18px; }}
        li {{ margin-bottom: 3px; font-size: 10pt; }}
    </style>
</head>
<body>

    <div class="header">
        <div class="name">周雨桥</div>
        <div class="info-bar">
            <span class="info-item">{icons['user']} 22岁</span>
            <span class="info-item">{icons['gender']} 男</span>
            <span class="info-item">{icons['phone']} 19560755561</span>
            <span class="info-item">{icons['mail']} 3468914095@qq.com</span>
        </div>
        <div class="photo-placeholder">个人照片<br>(建议粘贴)</div>
    </div>

    <div class="section-title">{icons['edu']} 教育背景</div>
    <div class="card">
        <div class="row-header">
            <div class="col-left">山东科技大学青岛校区</div>
            <div class="col-mid">计算机科学与技术（本科）</div>
            <div class="col-right">2023.09 - 2027.06</div>
        </div>
        <div class="course-list">
            <strong>主修课程：</strong>程序设计基础、离散数学、数据结构 (A)、操作系统、计算机组成原理、计算机网络、电路与电子技术、数字逻辑、算法设计与分析、数据库系统、编译原理、软件工程、人工智能、嵌入式系统原理与应用、面向对象程序设计（Java）
        </div>
    </div>

    <div class="section-title">{icons['project']} 项目经验</div>
    <div class="card">
        <div class="row-header">
            <div class="col-left">AI数字人视频生成系统</div>
            <div class="col-mid">语音算法开发</div>
            <div class="col-right">2026.01 - 2026.01</div>
        </div>
        <p class="description">
            参与开发一款基于深度学习的端到端“文本至数字人视频”生成系统。本人核心负责系统底层的文本转语音 (TTS) 与语音克隆模块，成功将复杂的开源大模型推理逻辑工程化落地，为全系统提供高拟真度的语音流服务。
        </p>
    </div>

    <div class="section-title">{icons['work']} 实习经验</div>
    <div class="card" style="margin-bottom: 8px;">
        <div class="row-header">
            <div class="col-left">中国移动山东公司青岛分公司</div>
            <div class="col-mid">业务运营</div>
            <div class="col-right">2025.07 - 2025.08</div>
        </div>
        <p class="description">
            负责维护线上用户答疑通道，基于高频问题分析并解决用户需求。协助新媒体进行数据采集与清洗，推进业务发展，为营销策略提供清晰数据支持，有效提升了客户转化率。
        </p>
    </div>
    <div class="card">
        <div class="row-header">
            <div class="col-left">山东科技大学</div>
            <div class="col-mid">算法工程师</div>
            <div class="col-right">2026.01 - 2026.01</div>
        </div>
        <p class="description">
            负责 Bert-VITS2 语音生成模块落地。深入研究 infer.py 推理逻辑，实现文本清洗、BERT 特征提取到音频生成的全流程封装。负责接口参数调优（如 SDP 占比、噪声比例等），显著提升合成自然度。
        </p>
    </div>

    <div class="section-title">{icons['award']} 荣誉证书</div>
    <div class="card">
        <ul>
            <li>第十五届蓝桥杯全国软件和信息技术专业人才大赛 省赛软件类C/C++ 大学B组 <strong>二等奖</strong></li>
            <li>第十六届蓝桥杯全国软件和信息技术专业人才大赛 省赛软件类C/C++ 大学B组 <strong>二等奖</strong></li>
        </ul>
    </div>

</body>
</html>
"""

# Save to PDF
output_pdf_path = "personalized_resume_zhouyuqiao.pdf"
HTML(string=html_content).write_pdf(output_pdf_path)
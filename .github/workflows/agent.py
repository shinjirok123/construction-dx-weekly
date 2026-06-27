import anthropic, json, os
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def research():
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system="あなたは土木・建設DXの専門リサーチャーです。日本語で回答してください。",
        messages=[{
            "role": "user",
            "content": """今週の土木・建設DX関連ニュースを調査して、以下のJSON形式のみで返してください。
{
  "updated": "YYYY-MM-DD",
  "summary": "今週の全体サマリー（200字）",
  "items": [
    {
      "category": "BIM/CIM|施工DX|インフラ管理|スタートアップ|政策・制度",
      "title": "タイトル",
      "summary": "要約（100字）",
      "impact": "high|medium|low",
      "source": "メディア名"
    }
  ]
}
JSONのみ返し、前後の説明文は不要です。"""
        }]
    )
    
    text = "".join(b.text for b in response.content if hasattr(b, "text"))
    data = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
    
    # HTMLダッシュボード生成
    generate_html(data)
    
    # データ保存（履歴）
    os.makedirs("data", exist_ok=True)
    with open(f"data/{data['updated']}.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_html(data):
    colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
    cards = ""
    for item in data["items"]:
        color = colors.get(item["impact"], "#6b7280")
        cards += f"""
        <div class="card">
          <div class="card-header">
            <span class="category">{item['category']}</span>
            <span class="impact" style="background:{color}">{item['impact'].upper()}</span>
          </div>
          <h3>{item['title']}</h3>
          <p>{item['summary']}</p>
          <small>📰 {item['source']}</small>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>建設DX Weekly</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Hiragino Sans',sans-serif; background:#0f172a; color:#e2e8f0; }}
  header {{ background:#1e293b; padding:24px 32px; border-bottom:1px solid #334155; }}
  header h1 {{ font-size:24px; color:#38bdf8; }}
  header p {{ color:#94a3b8; margin-top:4px; font-size:14px; }}
  .summary-box {{ margin:24px 32px; background:#1e293b; border-left:4px solid #38bdf8;
    padding:16px 20px; border-radius:8px; line-height:1.7; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
    gap:16px; padding:0 32px 32px; }}
  .card {{ background:#1e293b; border-radius:12px; padding:20px;
    border:1px solid #334155; transition:.2s; }}
  .card:hover {{ border-color:#38bdf8; transform:translateY(-2px); }}
  .card-header {{ display:flex; justify-content:space-between; margin-bottom:10px; }}
  .category {{ font-size:12px; color:#94a3b8; background:#0f172a;
    padding:2px 8px; border-radius:99px; }}
  .impact {{ font-size:11px; color:white; padding:2px 8px; border-radius:99px; font-weight:bold; }}
  h3 {{ font-size:15px; margin-bottom:8px; line-height:1.5; }}
  p {{ font-size:13px; color:#94a3b8; line-height:1.6; }}
  small {{ display:block; margin-top:10px; color:#64748b; font-size:12px; }}
</style>
</head>
<body>
<header>
  <h1>🏗️ 建設DX Weekly</h1>
  <p>更新日: {data['updated']} ｜ AI自動収集・要約</p>
</header>
<div class="summary-box">📋 {data['summary']}</div>
<div class="grid">{cards}</div>
</body>
</html>"""
    
    with open("index.html", "w") as f:
        f.write(html)

research()

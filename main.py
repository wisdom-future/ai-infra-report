import feedparser
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

# 替换为你的 Server 酱 SCKEY
WECHAT_SCKEY = "SCT301898TbWUGL3GetX3h0xujBTFdS45K"  # ← 填你的真实 SCKEY

def send_wechat(title, body):
    if not WECHAT_SCKEY or WECHAT_SCKEY == "SCT12345TAbc...":
        print("SCKEY 未配置，跳过推送")
        return
    try:
        data = urllib.parse.urlencode({'text': title, 'desp': body}).encode()
        req = urllib.request.Request(f'https://sctapi.ftqq.com/{WECHAT_SCKEY}.send', data)
        response = urllib.request.urlopen(req, timeout=10)
        result = response.read().decode('utf-8')
        print(f"推送结果: {result}")
    except Exception as e:
        print(f"推送失败: {e}")

def main():
    news = []
    seen_links = set()
    
    # 放宽查询，去掉 min_faves 限制
    queries = [
        'ai infrastructure OR gpu OR datacenter OR hyperscaler OR stargate',
        'nvidia OR openai OR aws OR azure OR "data center"',
        'blackwell OR gb200 OR h100 OR ai chip OR liquid cooling'
    ]
    
    print("开始抓取 AI Infrastructure 新闻...")
    
    for q in queries:
        url = f'https://rsshub.app/x/search/{urllib.parse.quote(q)}'
        print(f"正在查询: {q}")
        print(f"RSS URL: {url}")
        
        try:
            feed = feedparser.parse(url)
            entries_count = len(feed.entries)
            print(f"  → 抓到 {entries_count} 条原始帖")
        except Exception as e:
            print(f"  → 抓取失败: {e}")
            continue
        
        for e in feed.entries[:20]:
            link = e.link
            if link in seen_links:
                continue
            seen_links.add(link)
            
            # 解析发布时间
            try:
                pub = datetime(*e.published_parsed[:6])
            except:
                pub = datetime.now()
            
            # 只看最近 36 小时
            if pub < datetime.now() - timedelta(hours=36):
                continue
                
            text = (e.title or "") + " " + (e.summary or "")
            text = text.replace('\n', ' ').strip()
            
            # 提取点赞数（支持 K、千、万）
            likes = 0
            m = re.search(r'([\d,.]+) ?[Kk]? ?[Ll]ikes?', text, re.I)
            if m:
                val = m.group(1).replace('K','000').replace('k','000').replace(',','').replace('.','')
                try:
                    likes = int(float(val))
                except:
                    likes = 0
            
            title = text[:120]
            print(f"  - 候选: {title[:60]}... (点赞: {likes})")
            
            # 放宽入选条件
            if (likes >= 5 or 
                any(k in text.lower() for k in 
                    ['nvidia', 'openai', 'aws', 'azure', 'gpu', 'datacenter', 
                     'blackwell', 'stargate', 'ai infrastructure', 'liquid cooling', 'data center'])):
                
                news.append(f"**{title}**\n点赞: {likes} | {pub.strftime('%m/%d %H:%M')}\n[链接]({link})")
                print(f"  入选！")
    
    print(f"\n最终筛选出 {len(news)} 条关键新闻")
    
    # 无论有没有新闻，都发一条消息（确保你知道脚本在跑）
    if news:
        t = f"【AI Infra 早报 · {datetime.now().strftime('%m/%d')}】"
        b = '\n\n---\n\n'.join(news[:10])
        send_wechat(t, b)
    else:
        t = "AI Infra 早报 · 运行正常"
        b = ("今日暂无高赞 AI 基础设施新闻（点赞 ≥5 或含关键词）。\n"
              "脚本运行正常，明天 8:00 继续推送！\n"
              "如需调整关键词，请修改 `main.py` 中的 `queries` 列表。")
        send_wechat(t, b)

if __name__ == '__main__':
    main()

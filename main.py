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
    
    # 超宽松关键词组合（覆盖所有 AI 基础设施热点）
    queries = [
        'ai infrastructure OR gpu OR datacenter OR hyperscaler OR stargate OR power OR cooling',
        'nvidia OR openai OR aws OR azure OR google OR microsoft OR "data center" OR "ai chip"',
        'blackwell OR gb200 OR h100 OR h200 OR b200 OR liquid cooling OR rack OR cluster',
        'energy OR electricity OR nvidia OR tesla OR "ai training" OR "inference"',
        'cloud OR aws OR azure OR gcp OR oracle OR "ai cloud"'
    ]
    
    print("开始抓取 AI Infrastructure 新闻（过去 3 天）...")
    
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
        
        for e in feed.entries[:30]:  # 每查询看前30条
            link = e.link
            if link in seen_links:
                continue
            seen_links.add(link)
            
            # 解析发布时间
            try:
                pub = datetime(*e.published_parsed[:6])
            except:
                pub = datetime.now()
            
            # 扩大时间窗：过去 3 天（72 小时）
            if pub < datetime.now() - timedelta(hours=72):
                continue
                
            text = (e.title or "") + " " + (e.summary or "")
            text = text.replace('\n', ' ').strip()
            
            # 提取点赞数（支持 K、千、万、逗号、小数点）
            likes = 0
            m = re.search(r'([\d,.]+) ?[Kk]? ?[Ll]ikes?', text, re.I)
            if m:
                val = m.group(1).replace('K','000').replace('k','000').replace(',','').replace('.','')
                try:
                    likes = int(float(val))
                except:
                    likes = 0
            
            title = text[:150]  # 标题更长
            print(f"  - 候选: {title[:70]}... (点赞: {likes})")
            
            # 超宽松入选条件：点赞 >= 1 或含任意关键词
            if (likes >= 1 or 
                any(k in text.lower() for k in [
                    'nvidia', 'openai', 'aws', 'azure', 'google', 'microsoft',
                    'gpu', 'datacenter', 'blackwell', 'stargate', 'h100', 'h200',
                    'liquid cooling', 'power', 'energy', 'ai infrastructure',
                    'cloud', 'cluster', 'training', 'inference', 'chip', 'rack'
                ])):
                
                news.append(f"**{title}**\n点赞: {likes} | {pub.strftime('%m/%d %H:%M')}\n[链接]({link})")
                print(f"  入选！")
    
    print(f"\n最终筛选出 {len(news)} 条关键新闻（过去 3 天）")
    
    # 无论如何都发消息
    if news:
        t = f"【AI Infra 早报 · {datetime.now().strftime('%m/%d')}】（3天汇总）"
        b = '\n\n---\n\n'.join(news[:15])  # 最多15条
        send_wechat(t, b)
    else:
        t = "AI Infra 早报 · 运行正常"
        b = ("过去 3 天暂无符合条件的 AI 基础设施新闻。\n"
              "脚本运行正常，明天 8:00 继续推送！\n"
              "当前过滤：点赞 ≥1 或含关键词，时间窗 72 小时。")
        send_wechat(t, b)

if __name__ == '__main__':
    main()

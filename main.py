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
    
    # 关键账户 + 宽松搜索（用户feed更稳）
    sources = [
        # 用户feed（高优先，抓官方/影响者帖子）
        ('nvidia', 'https://rsshub.app/x/user/nvidia'),
        ('OpenAI', 'https://rsshub.app/x/user/OpenAI'),
        ('awscloud', 'https://rsshub.app/x/user/awscloud'),
        ('NVIDIADC', 'https://rsshub.app/x/user/NVIDIADC'),
        ('NVIDIAAI', 'https://rsshub.app/x/user/NVIDIAAI'),
        # 备用搜索（去min_faves）
        ('ai infrastructure OR gpu OR datacenter', 'https://rsshub.app/x/search/ai%20infrastructure%20OR%20gpu%20OR%20datacenter'),
        ('nvidia OR blackwell OR stargate', 'https://rsshub.app/x/search/nvidia%20OR%20blackwell%20OR%20stargate'),
        ('openai OR aws OR azure OR hyperscaler', 'https://rsshub.app/x/search/openai%20OR%20aws%20OR%20azure%20OR%20hyperscaler')
    ]
    
    print("开始抓取 AI Infrastructure 新闻（过去 3 天）...")
    
    for name, url in sources:
        print(f"正在查询源: {name} - {url}")
        
        try:
            feed = feedparser.parse(url)
            entries_count = len(feed.entries)
            print(f"  → 抓到 {entries_count} 条原始帖")
        except Exception as e:
            print(f"  → 抓取失败: {e}")
            continue
        
        for e in feed.entries[:25]:  # 每源前25条
            link = e.link
            if link in seen_links:
                continue
            seen_links.add(link)
            
            # 解析时间
            try:
                pub = datetime(*e.published_parsed[:6])
            except:
                pub = datetime.now()
            
            # 3天窗
            if pub < datetime.now() - timedelta(hours=72):
                continue
                
            text = (e.title or "") + " " + (e.summary or "")
            text = text.replace('\n', ' ').strip()
            
            # 点赞提取
            likes = 0
            m = re.search(r'([\d,.]+) ?[Kk]? ?[Ll]ikes?', text, re.I)
            if m:
                val = m.group(1).replace('K','000').replace('k','000').replace(',','').replace('.','')
                try:
                    likes = int(float(val))
                except:
                    likes = 0
            
            title = text[:150]
            print(f"  - 候选: {title[:70]}... (点赞: {likes})")
            
            # 入选条件
            if (likes >= 1 or 
                any(k in text.lower() for k in [
                    'nvidia', 'openai', 'aws', 'azure', 'gpu', 'datacenter', 
                    'blackwell', 'stargate', 'h100', 'h200', 'liquid cooling', 
                    'power', 'energy', 'ai infrastructure', 'cloud', 'cluster', 
                    'training', 'inference', 'chip', 'rack', 'hyperscaler'
                ])):
                
                news.append(f"**{name}: {title}**\n点赞: {likes} | {pub.strftime('%m/%d %H:%M')}\n[链接]({link})")
                print(f"  ✓ 入选！")
    
    print(f"\n最终筛选出 {len(news)} 条关键新闻")
    
    if news:
        t = f"【AI Infra 早报 · {datetime.now().strftime('%m/%d')}】（3天汇总）"
        b = '\n\n---\n\n'.join(news[:15])
        send_wechat(t, b)
    else:
        t = "AI Infra 早报 · 运行正常"
        b = ("过去 3 天暂无符合条件的新闻（已监控 @nvidia 等账户）。\n"
              "脚本运行正常，明天 8:00 继续！\n"
              "调试: 检查日志源是否抓到帖子。")
        send_wechat(t, b)

if __name__ == '__main__':
    main()

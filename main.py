import feedparser
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

# 替换为你的Server酱SCKEY
WECHAT_SCKEY = "SCT301898TbWUGL3GetX3h0xujBTFdS45K"  # ← 这里填你的SCKEY

def send_wechat(title, body):
    if not WECHAT_SCKEY:
        print("No SCKEY, skipping send")
        return
    data = urllib.parse.urlencode({'text': title, 'desp': body}).encode()
    req = urllib.request.Request(f'https://sctapi.ftqq.com/{WECHAT_SCKEY}.send', data)
    urllib.request.urlopen(req)

def main():
    news = []
    seen_links = set()
    queries = [
        'ai infrastructure OR gpu OR datacenter min_faves:50',
        'nvidia OR gb300 OR h200 min_faves:30',
        'stargate OR hyperscaler OR "data center"'
    ]
    for q in queries:
        url = f'https://rsshub.app/x/search/{urllib.parse.quote(q)}'
        feed = feedparser.parse(url)
        for e in feed.entries[:15]:
            link = e.link
            if link in seen_links:
                continue
            seen_links.add(link)
            try:
                pub = datetime(*e.published_parsed[:6])
            except:
                pub = datetime.now()
            if pub < datetime.now() - timedelta(hours=30):
                continue
            text = (e.title + ' ' + (e.summary or '')).replace('\n', ' ')
            likes = 0
            m = re.search(r'([\d,.]+) ?[Kk]? ?[Ll]ikes?', text)
            if m:
                val = m.group(1).replace('K', '000').replace('k', '000').replace(',', '')
                likes = int(float(val))
            title = text[:100].strip()
            if likes >= 30 or any(k in text.lower() for k in ['nvidia', 'openai', 'gpu', 'microsoft', 'datacenter']):
                news.append(f"**{title}**\n点赞: {likes} | {pub.strftime('%m/%d %H:%M')}\n[链接]({link})")
    if news:
        t = f"【AI Infra 早报 · {datetime.now().strftime('%m/%d')}】"
        b = '\n\n---\n\n'.join(news[:10])
        send_wechat(t, b)
        print(f"Sent {len(news)} news items")
    else:
        print("No key news found")

if __name__ == '__main__':
    main()

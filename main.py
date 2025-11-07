import requests
import re
from datetime import datetime, timedelta

# ================== 你的密钥（已填入）==================
WECHAT_SCKEY = "SCT301898TbWUGL3GetX3h0xujBTFdS45K"  # Server酱
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJkc2QEAAAAAxlP2DoZsn5v5rDjicbJD74bW58A%3Diy3FKAKrnPEoJktUpDZktdwsDs8gXAASEaJryaRCWrLwpUSQ1K"  # X Bearer Token
# =====================================================

def send_wechat(title, body):
    if not WECHAT_SCKEY:
        print("SCKEY 未配置")
        return
    try:
        data = {'text': title, 'desp': body}
        response = requests.post(f'https://sctapi.ftqq.com/{WECHAT_SCKEY}.send', data=data, timeout=15)
        result = response.json()
        if result.get('code') == 0:
            print(f"推送成功: {result.get('data', {}).get('pushid')}")
        else:
            print(f"推送失败: {result}")
    except Exception as e:
        print(f"推送异常: {e}")

def fetch_x_posts():
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=3)

    query = '(ai infrastructure OR gpu OR datacenter OR hyperscaler OR stargate OR "ai chip" OR "liquid cooling" OR "data center") min_faves:5'
    
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        'query': query,
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'max_results': 20,
        'tweet.fields': 'public_metrics,created_at,author_id',
        'expansions': 'author_id',
        'user.fields': 'username,name'
    }

    news = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        data = response.json()

        if 'data' not in data:
            print(f"API返回无数据: {data}")
            return news

        users = {u['id']: u for u in data.get('includes', {}).get('users', [])}

        for tweet in data['data']:
            author_id = tweet['author_id']
            author = users.get(author_id, {})
            username = author.get('username', 'unknown')
            name = author.get('name', username)

            likes = tweet['public_metrics']['like_count']
            text = tweet['text'].replace('\n', ' ').strip()
            created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
            link = f"https://x.com/{username}/status/{tweet['id']}"

            title = text[:120] + "..." if len(text) > 120 else text

            news.append(
                f"**{name} (@{username})**\n{title}\n"
                f"点赞: {likes} | {created_at.strftime('%m/%d %H:%M')}\n"
                f"[查看原文]({link})"
            )

        print(f"成功抓取 {len(news)} 条真实新闻")
        return news[:15]

    except Exception as e:
        print(f"API请求失败: {e}")
        return []

def main():
    print("开始抓取 AI Infrastructure 早报（过去3天）...")
    news = fetch_x_posts()

    if news:
        title = f"【AI Infra 早报 · {datetime.now().strftime('%m/%d')}】"
        body = "\n\n---\n\n".join(news)
    else:
        title = "AI Infra 早报 · 运行正常"
        body = "过去3天暂无符合条件的高赞新闻（min_faves:5）。\n脚本运行正常，明天8:00继续！"

    send_wechat(title, body)

if __name__ == '__main__':
    main()

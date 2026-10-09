import requests
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime, timezone
import hashlib

API_URL = "https://gondola-pastel.microcms.io/api/v1/blogs"
SITE_URL = "https://gondola-pastel.com/"
OUTPUT = "gondola_pastel.xml"

API_KEY = "w1clDzoaUP8ogpNhe3BouwT1tPrVdJEPBAH4"

HEADERS = {
    "X-API-KEY": API_KEY,
    "User-Agent": "Mozilla/5.0"
}


def make_guid(url):
    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()


def parse_datetime(value):
    # microCMS:
    # 2024-06-27T00:15:55.218Z
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


response = requests.get(
    API_URL,
    headers=HEADERS,
    params={
        "limit": 100,
        "orders": "-publishedAt"
    },
    timeout=30
)

print("API HTTP:", response.status_code)

response.raise_for_status()

data = response.json()

contents = data.get("contents", [])

items = []

for post in contents:

    post_id = post.get("id")
    title = post.get("title", "").strip()
    published_at = post.get("publishedAt")

    if not post_id:
        continue

    if not title:
        continue

    if not published_at:
        continue

    article_url = (
        f"https://gondola-pastel.com/"
        f"news.html?id={post_id}"
    )

    dt = parse_datetime(published_at)

    items.append({
        "title": title,
        "link": article_url,
        "guid": make_guid(article_url),
        "pubDate": format_datetime(dt),
        "sort_date": dt
    })


items.sort(
    key=lambda x: x["sort_date"],
    reverse=True
)


rss = ET.Element(
    "rss",
    version="2.0"
)

channel = ET.SubElement(
    rss,
    "channel"
)

ET.SubElement(
    channel,
    "title"
).text = "ゴンドラ・パステル NEWs"

ET.SubElement(
    channel,
    "link"
).text = SITE_URL

ET.SubElement(
    channel,
    "description"
).text = "ゴンドラ・パステル公式サイトの新着情報"

ET.SubElement(
    channel,
    "language"
).text = "ja"

ET.SubElement(
    channel,
    "lastBuildDate"
).text = format_datetime(
    datetime.now(timezone.utc)
)


for data in items:

    item = ET.SubElement(
        channel,
        "item"
    )

    ET.SubElement(
        item,
        "title"
    ).text = data["title"]

    ET.SubElement(
        item,
        "link"
    ).text = data["link"]

    ET.SubElement(
        item,
        "description"
    ).text = "ゴンドラ・パステル NEWs"

    ET.SubElement(
        item,
        "pubDate"
    ).text = data["pubDate"]

    guid = ET.SubElement(
        item,
        "guid",
        isPermaLink="false"
    )

    guid.text = data["guid"]


tree = ET.ElementTree(rss)

ET.indent(
    tree,
    space="  "
)

tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)


print()
print("RSS作成成功")
print("取得件数:", len(items))
print()
print("RSS先頭記事:")

for i, item in enumerate(items[:10], 1):

    print()
    print(f"[{i}] {item['title']}")
    print("    ", item["pubDate"])
    print("    ", item["link"])
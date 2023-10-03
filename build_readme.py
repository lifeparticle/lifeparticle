from imgurpython.helpers.error import ImgurClientError
from imgurpython import ImgurClient
import requests
import pathlib
import random
import json
import sys
import re
import os

# Constants
ROOT_DIR = pathlib.Path(__file__).parent.resolve()
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
PROGRAMMER_HUMOR_LINK = "https://imgur.com/r/ProgrammerHumor/{}"
MEDIUM_RSS_LINK = "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/@lifeparticle"

def create_imgur_link(id, link):
    return f'<a href="{PROGRAMMER_HUMOR_LINK.format(id)}"><img max-height="400" width="350" src="{link}"></a>'

def update_programmer_humor_img(name):
    try:
        client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
        credits = client.credits
        if credits["UserRemaining"] > 0:
            items = client.subreddit_gallery(name, sort="top", window="week", page=0)
            for item in items:
                if not item.link.endswith((".mp4", ".gif")):
                    return create_imgur_link(item.id, item.link)
        else:
            print("Not enough credits remaining to make the request.")
            
        return create_imgur_link("SV767tT", "SV767tT")

    except ImgurClientError as e:
        print(e.error_message)

def replace_chunk(content, marker, chunk, inline=False):
    pattern = re.compile(
        f"<!-- {marker} starts -->.*<!-- {marker} ends -->",
        re.DOTALL,
    )
    if not inline:
        chunk = f"\n{chunk}\n"
    chunk = f"<!-- {marker} starts -->{chunk}<!-- {marker} ends -->"
    return pattern.sub(chunk, content)

def fetch_blog_posts(link):
    result = []
    response = requests.get(link)
    if response.status_code == 200:
        posts = json.loads(response.text)["items"]
        for post in posts:
            if len(post["categories"]) != 0:
                post["pubDate"] = post["pubDate"].split()[0]
                result.append(post)
    elif response.status_code == 404:
        print(f"Not Found: {link}")
    return result

if __name__ == "__main__":
    readme = ROOT_DIR / "README.md"
    readme_contents = readme.open().read()
    rewritten = readme_contents
    rewritten = replace_chunk(rewritten, "programmer_humor_img", update_programmer_humor_img("ProgrammerHumor"))

    posts = fetch_blog_posts(MEDIUM_RSS_LINK)
    if posts:
        posts_md = "\n".join([f"* [{post['title']}]({post['link']}) <br/> <sub>{post['pubDate']}</sub>" for post in posts])
        rewritten = replace_chunk(rewritten, "blog", posts_md)

    readme.open("w").write(rewritten)
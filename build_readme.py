import requests
import pathlib
import json
import sys
import re
import os

root = pathlib.Path(__file__).parent.resolve()
link = "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/@lifeparticle"

def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def fetch_blog_posts():
	result = []
	response = requests.get(link)
	if response.status_code == 200:
		posts = json.loads(response.text)["items"]
		for post in posts:
			if len(post["categories"]) != 0:
				result.append(post)
	elif response.status_code == 404:
		print('Not Found: ') + link
	return result

if __name__ == "__main__":
	readme = root / "README.md"

	posts = fetch_blog_posts()
	if len(posts) != 0:
		readme_contents = readme.open().read()
		rewritten = readme_contents

		posts_md = "\n".join(
			["* [{title}]({link}) - {pubDate}".format(**post) for post in posts]
		)

		rewritten = replace_chunk(rewritten, "blog", posts_md)
		readme.open("w").write(rewritten)
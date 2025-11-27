#!/usr/bin/env python3
"""
Update index.html with exact titles and local image paths
"""
import json
import re

# Read the article data
with open('article-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

titles = data.get('titles', {})
images = data.get('images', {})

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Update titles
title_pattern = r'(const articleTitles = \{)(.*?)(\};)'
title_match = re.search(title_pattern, html_content, re.DOTALL)

if title_match:
    new_titles = '        const articleTitles = {\n'
    for url, title in titles.items():
        # Decode HTML entities
        title = title.replace('&#x27;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        title = title.replace('&quot;', '"').replace('&nbsp;', ' ')
        # Escape quotes in title
        escaped_title = title.replace('\\', '\\\\').replace('"', '\\"')
        new_titles += f'            "{url}": "{escaped_title}",\n'
    new_titles = new_titles.rstrip(',\n') + '\n        };'
    html_content = html_content[:title_match.start()] + new_titles + html_content[title_match.end():]

# Update images
image_pattern = r'(const articleImages = \{)(.*?)(\};)'
image_match = re.search(image_pattern, html_content, re.DOTALL)

if image_match:
    new_images = '        const articleImages = {\n'
    for url, filename in images.items():
        new_images += f'            "{url}": "{filename}",\n'
    new_images = new_images.rstrip(',\n') + '\n        };'
    html_content = html_content[:image_match.start()] + new_images + html_content[image_match.end():]

# Write updated HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✓ Updated index.html with exact titles and local image paths")
print(f"  - {len(titles)} titles updated")
print(f"  - {len(images)} images mapped")


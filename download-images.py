#!/usr/bin/env python3
"""
Download article images from Lleverage blog posts
"""
import urllib.request
import urllib.parse
import re
import json
import time
import os

articles = [
    "https://www.lleverage.ai/blog/ai-automation-in-the-netherlands-how-dutch-businesses-are-leading-europes-automation-revolution-in-2025",
    "https://www.lleverage.ai/blog/ai-automation-in-france-how-french-businesses-are-leading-europes-technology-renaissance-in-2025",
    "https://www.lleverage.ai/blog/ai-automation-in-the-uk-how-british-businesses-are-transforming-operations-in-2025",
    "https://www.lleverage.ai/customer-stories/how-koninklijke-dekker-modernized-its-order-intake-with-ai-automation",
    "https://www.lleverage.ai/customer-stories/how-j-kisch-zonen-uses-ai-to-scale-its-130-year-old-furniture-supply-business",
    "https://www.lleverage.ai/blog/how-ai-automation-solves-your-erp-tms-problems-from-manual-work-to-intelligent-operations",
    "https://www.lleverage.ai/blog/erp-implementation-failure-why-75-fail-at-189-over-budget-and-how-ai-automation-fills-the-gaps",
    "https://www.lleverage.ai/blog/erp-ai-integration-guide-lleverage-business-central-sap-infor-dynamics-365-f-o-afas-navision",
    "https://www.lleverage.ai/blog/the-eu500k-question-what-your-erp-system-isnt-telling-you-about-its-hidden-costs-in-2025",
    "https://www.lleverage.ai/blog/the-death-of-data-entry-why-manual-work-is-becoming-extinct-in-2025",
    "https://www.lleverage.ai/blog/ai-document-processing-how-ai-is-making-manual-data-entry-obsolete",
    "https://www.lleverage.ai/blog/the-roi-of-ai-automation-how-to-measure-success-in-your-business-2025-guide",
    "https://www.lleverage.ai/blog/how-to-transition-from-manual-workflows-to-ai-powered-automation-a-step-by-step-guide-for-2025",
    "https://www.lleverage.ai/blog/the-6-back-office-automations-that-wholesale-manufacturing-and-logistics-companies-cant-afford-to-ignore",
    "https://www.lleverage.ai/blog/the-state-of-ai-manufacturing-in-europe-8-game-changing-automations-transforming-the-industry",
    "https://www.lleverage.ai/blog/ai-security-and-compliance-what-european-businesses-need-to-consider-in-2025"
]

def fetch_with_proxy(url):
    """Fetch HTML using CORS proxy"""
    proxies = [
        f"https://api.allorigins.win/raw?url={urllib.parse.quote(url)}",
        f"https://corsproxy.io/?{urllib.parse.quote(url)}",
    ]
    
    for proxy_url in proxies:
        try:
            req = urllib.request.Request(proxy_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
            with urllib.request.urlopen(req, timeout=20) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"    Proxy failed: {e}")
            continue
    
    # Try direct as last resort
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"    Direct fetch failed: {e}")
        return None

def extract_image_url(html, base_url):
    """Extract image URL from HTML"""
    # Try multiple regex patterns
    patterns = [
        r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']',
        r'property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            image_url = match.group(1).strip()
            if image_url:
                # Make absolute URL
                if not image_url.startswith('http'):
                    parsed = urllib.parse.urlparse(base_url)
                    if image_url.startswith('//'):
                        image_url = parsed.scheme + ':' + image_url
                    elif image_url.startswith('/'):
                        image_url = parsed.scheme + '://' + parsed.netloc + image_url
                    else:
                        image_url = parsed.scheme + '://' + parsed.netloc + '/' + image_url
                return image_url
    
    return None

def extract_title(html):
    """Extract exact title from HTML"""
    # Try og:title first (usually more accurate)
    patterns = [
        r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:title["\']',
        r'<title>([^<]+)</title>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remove " | Lleverage" suffix if present
            title = re.sub(r'\s*\|\s*Lleverage\s*$', '', title, flags=re.IGNORECASE)
            # Decode HTML entities
            title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            title = title.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
            return title.strip()
    
    return None

def download_image(image_url, filename):
    """Download image from URL"""
    try:
        req = urllib.request.Request(image_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.lleverage.ai/'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False

def main():
    results = {
        'titles': {},
        'images': {}
    }
    
    print("Fetching article data...\n")
    
    for i, url in enumerate(articles, 1):
        slug = url.split('/')[-1]
        safe_slug = re.sub(r'[^a-zA-Z0-9-]', '-', slug[:50])
        filename = f"article-{i:02d}-{safe_slug}.jpg"
        
        print(f"[{i}/{len(articles)}] Processing: {slug[:60]}...")
        
        # Fetch HTML
        html = fetch_with_proxy(url)
        if not html:
            print(f"    ✗ Failed to fetch HTML")
            continue
        
        # Extract title
        title = extract_title(html)
        if title:
            results['titles'][url] = title
            print(f"    ✓ Title: {title[:60]}...")
        else:
            print(f"    ✗ No title found")
        
        # Extract and download image
        image_url = extract_image_url(html, url)
        if image_url:
            print(f"    ✓ Image URL: {image_url[:60]}...")
            if download_image(image_url, filename):
                results['images'][url] = filename
                print(f"    ✓ Saved as: {filename}")
            else:
                print(f"    ✗ Failed to download image")
        else:
            print(f"    ✗ No image URL found")
        
        print()
        time.sleep(1)  # Be nice to the server
    
    # Save results
    with open('article-data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to article-data.json")
    print(f"✓ Titles found: {len(results['titles'])}")
    print(f"✓ Images downloaded: {len(results['images'])}")

if __name__ == '__main__':
    main()


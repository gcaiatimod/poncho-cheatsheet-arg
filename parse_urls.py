import urllib.request
def fetch_css(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Fetching {url}")
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

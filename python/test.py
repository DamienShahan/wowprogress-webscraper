import httpx
client = httpx.Client(http2=True)
response = client.get("https://www.wowprogress.com/pve/rating/next/-1/?raids_week=1-2")

print(response.status_code)
print(response.text)
import requests
import json

r = requests.post('http://localhost:8000/api/ai/recommend/stream', 
    json={'query': '心情不好，随便看看', 'max_results': 3}, 
    stream=True)
print(f"Status: {r.status_code}")

for line in r.iter_lines():
    if line:
        decoded = line.decode()
        print(decoded[:150] if len(decoded) > 150 else decoded)

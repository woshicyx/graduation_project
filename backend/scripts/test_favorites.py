import requests
import json

# 1. 注册测试用户
print("=== 1. 注册测试用户 ===")
r = requests.post('http://localhost:8000/api/auth/register', json={
    'email': 'test_api_user2@example.com',
    'username': 'test_api_user2',
    'password': 'test123456',
    'confirm_password': 'test123456'
})
print(f"注册: {r.status_code}")
if r.status_code not in [200, 201]:
    print(f"  响应: {r.json()}")

# 2. 登录获取token (使用 identifier)
print("\n=== 2. 登录获取token ===")
r = requests.post('http://localhost:8000/api/auth/login', json={
    'identifier': 'test_api_user2',
    'password': 'test123456'
})
print(f"登录: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    token = data.get('access_token')
    print(f"  Token获取成功: {token[:30]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. 添加收藏
    print("\n=== 3. 添加收藏 (movie_id=550) ===")
    r = requests.post('http://localhost:8000/api/users/me/favorites/550', 
        json={'action': 'like'},
        headers=headers)
    print(f"添加收藏: {r.status_code}")
    print(f"  响应: {r.json()}")
    
    # 4. 获取收藏列表
    print("\n=== 4. 获取收藏列表 ===")
    r = requests.get('http://localhost:8000/api/users/me/favorites', headers=headers)
    print(f"获取收藏: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  收藏数量: {data.get('total_count', 0)}")
        print(f"  收藏列表: {json.dumps(data.get('favorites', [])[:2], ensure_ascii=False)}")
    
    # 5. 添加浏览历史
    print("\n=== 5. 添加浏览历史 (movie_id=550) ===")
    r = requests.post('http://localhost:8000/api/users/me/watch-history/550', headers=headers)
    print(f"添加浏览: {r.status_code}")
    print(f"  响应: {r.json()}")
    
    # 6. 获取浏览历史
    print("\n=== 6. 获取浏览历史 ===")
    r = requests.get('http://localhost:8000/api/users/me/watch-history', headers=headers)
    print(f"获取浏览: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  历史数量: {len(data)}")
        if data:
            print(f"  第一条: {json.dumps(data[0], ensure_ascii=False)}")
else:
    print(f"  响应: {r.json()}")

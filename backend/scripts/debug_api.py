import requests
import json
import traceback

# 登录获取token
print("=== 登录获取token ===")
r = requests.post('http://localhost:8000/api/auth/login', json={
    'identifier': 'test_api_user2',
    'password': 'test123456'
})
print(f"登录: {r.status_code}")
if r.status_code == 200:
    token = r.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 获取收藏列表（带详细错误信息）
    print("\n=== 获取收藏列表 ===")
    try:
        r = requests.get('http://localhost:8000/api/users/me/favorites', headers=headers)
        print(f"状态码: {r.status_code}")
        print(f"响应: {r.text}")
    except Exception as e:
        print(f"异常: {e}")
        traceback.print_exc()
    
    # 获取浏览历史（带详细错误信息）
    print("\n=== 获取浏览历史 ===")
    try:
        r = requests.get('http://localhost:8000/api/users/me/watch-history', headers=headers)
        print(f"状态码: {r.status_code}")
        print(f"响应: {r.text}")
    except Exception as e:
        print(f"异常: {e}")
        traceback.print_exc()

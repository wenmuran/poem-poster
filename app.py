# === 新增：离线备胎诗词库 (防止断网报错) ===
def get_offline_poem():
    offline_poems = [
        {"content": "粗缯大布裹生涯，腹有诗书气自华。", "origin": {"title": "和董传留别", "author": "苏轼", "dynasty": "宋"}},
        {"content": "晚来天欲雪，能饮一杯无？", "origin": {"title": "问刘十九", "author": "白居易", "dynasty": "唐"}},
        {"content": "人生天地间，忽如远行客。", "origin": {"title": "青青陵上柏", "author": "佚名", "dynasty": "汉"}},
        {"content": "世事一场大梦，人生几度秋凉。", "origin": {"title": "西江月", "author": "苏轼", "dynasty": "宋"}},
        {"content": "莫听穿林打叶声，何妨吟啸且徐行。", "origin": {"title": "定风波", "author": "苏轼", "dynasty": "宋"}},
        {"content": "行到水窮處，坐看雲起時。", "origin": {"title": "终南别业", "author": "王维", "dynasty": "唐"}},
        {"content": "醉后不知天在水，满船清梦压星河。", "origin": {"title": "题龙阳县青草湖", "author": "唐温如", "dynasty": "元"}},
        {"content": "休对故人思故国，且将新火试新茶。诗酒趁年华。", "origin": {"title": "望江南", "author": "苏轼", "dynasty": "宋"}}
    ]
    return random.choice(offline_poems)

# === 修改后：带重试和伪装的获取函数 ===
def get_daily_poem():
    url = "https://v1.jinrishici.com/all.json"
    # 伪装成浏览器，防止被拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        # verify=False: 忽略 SSL 证书错误（解决国外服务器连接国内API的常见报错）
        # timeout=3: 3秒连不上就放弃，直接用备胎，不让用户等太久
        response = requests.get(url, headers=headers, timeout=3, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            # 简单的校验，确保数据格式没问题
            if 'content' in data:
                return data
    except Exception as e:
        # 这里可以打印错误方便调试，但在网页版里我们直接静默失败，启用备胎
        print(f"API连接失败: {e}")
    
    # 如果上面的 API 失败了，运行到这里，返回离线诗词
    print("启动离线备用诗词")
    return get_offline_poem()

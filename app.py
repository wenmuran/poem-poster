import streamlit as st
import requests
import textwrap
import random
from PIL import Image, ImageDraw, ImageFont
import datetime
import io

# === 配置区域 (简化版，直接写在代码里方便上传) ===
BG_COLORS = ["#F0C239", "#B2D235", "#F2E6CE", "#D1C7B7", "#88ADA6"]
FONT_PATH = "font.ttf"  # 确保字体文件也上传了
TEXT_COLOR = (50, 50, 50)
WIDTH, HEIGHT = 1080, 1920

# === 设置网页标题 ===
st.set_page_config(page_title="每日诗词海报", page_icon="📜")
st.title("📜 每日诗词海报生成器")
st.write("点击下方按钮，生成今天的专属诗词日签。")


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


# === 新增：离线备胎诗词库 (防止断网报错) ===
def get_offline_poem():
    offline_poems = [
        {"content": "粗缯大布裹生涯，腹有诗书气自华。",
         "origin": {"title": "和董传留别", "author": "苏轼", "dynasty": "宋"}},
        {"content": "晚来天欲雪，能饮一杯无？", "origin": {"title": "问刘十九", "author": "白居易", "dynasty": "唐"}},
        {"content": "人生天地间，忽如远行客。", "origin": {"title": "青青陵上柏", "author": "佚名", "dynasty": "汉"}},
        {"content": "世事一场大梦，人生几度秋凉。", "origin": {"title": "西江月", "author": "苏轼", "dynasty": "宋"}},
        {"content": "莫听穿林打叶声，何妨吟啸且徐行。", "origin": {"title": "定风波", "author": "苏轼", "dynasty": "宋"}},
        {"content": "行到水窮處，坐看雲起時。", "origin": {"title": "终南别业", "author": "王维", "dynasty": "唐"}},
        {"content": "醉后不知天在水，满船清梦压星河。",
         "origin": {"title": "题龙阳县青草湖", "author": "唐温如", "dynasty": "元"}},
        {"content": "休对故人思故国，且将新火试新茶。诗酒趁年华。",
         "origin": {"title": "望江南", "author": "苏轼", "dynasty": "宋"}}
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

def generate_image():
    # 1. 获取数据
    data = get_daily_poem()
    if not data:
        st.error("获取诗词失败，请重试")
        return None

    content = data.get('content', '暂无诗句')
    origin = data.get('origin', {})

    if isinstance(origin, dict):
        title = f"《{origin.get('title', '无题')}》"
        author = f"{origin.get('dynasty', '')} · {origin.get('author', '佚名')}"
    else:
        title = "《每日一诗》"
        author = str(origin)

    # 2. 绘图
    bg_hex = random.choice(BG_COLORS)
    image = Image.new('RGB', (WIDTH, HEIGHT), color=hex_to_rgb(bg_hex))
    draw = ImageDraw.Draw(image)

    try:
        font_main = ImageFont.truetype(FONT_PATH, size=int(WIDTH / 11))
        font_meta = ImageFont.truetype(FONT_PATH, size=int(WIDTH / 24))
        font_date = ImageFont.truetype(FONT_PATH, size=int(WIDTH / 28))
    except:
        st.error("缺少字体文件 font.ttf")
        return None

    # 绘制正文
    lines = textwrap.wrap(content, width=10)
    h = HEIGHT * 0.3
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        draw.text(((WIDTH - (bbox[2] - bbox[0])) / 2, h), line, font=font_main, fill=TEXT_COLOR)
        h += int(WIDTH / 11) + 30

    # 绘制落款
    h += 80
    bbox = draw.textbbox((0, 0), title, font=font_meta)
    draw.text(((WIDTH - (bbox[2] - bbox[0])) / 2, h), title, font=font_meta, fill=TEXT_COLOR)
    h += 60
    bbox = draw.textbbox((0, 0), author, font=font_meta)
    draw.text(((WIDTH - (bbox[2] - bbox[0])) / 2, h), author, font=font_meta, fill=TEXT_COLOR)

    # 绘制日期
    today = datetime.datetime.now()
    date_text = f"{today.strftime('%Y.%m.%d')} | {['一', '二', '三', '四', '五', '六', '日'][today.weekday()]}"
    bbox = draw.textbbox((0, 0), date_text, font=font_date)
    draw.text(((WIDTH - (bbox[2] - bbox[0])) / 2, HEIGHT - 150), date_text, font=font_date, fill=(80, 80, 80))

    return image


# === 网页交互逻辑 ===
if st.button("🎨 生成今日海报", type="primary"):
    with st.spinner('正在挥毫泼墨...'):
        img = generate_image()
        if img:
            # 展示图片
            st.image(img, caption="长按图片可保存", use_container_width=True)

            # 提供下载按钮
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            byte_im = buf.getvalue()
            st.download_button(
                label="⬇️ 下载原图",
                data=byte_im,
                file_name=f"poem_{datetime.date.today()}.jpg",
                mime="image/jpeg"
            )

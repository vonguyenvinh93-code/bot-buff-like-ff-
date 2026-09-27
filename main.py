import os
import threading
from flask import Flask
import discord
from discord import app_commands
import requests

# 1. TẠO WEB SERVER ĐỂ GIỮ BOT KHÔNG BỊ NGỦ
app = Flask('')

@app.route('/')
def home():
    return "Bot Free Fire đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# 2. CẤU HÌNH DISCORD BOT
API_URL = "https://free-fire-like-api.p.rapidapi.com/like"
API_KEY = "API_KEY_CUA_BAN"  # Thay bằng API Key của bạn nếu có
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN") # Lấy Token từ biến môi trường của Render

class FreeFireBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = FreeFireBot()

@client.event
async def on_ready():
    print(f"Bot đã kết nối thành công: {client.user}")

@client.tree.command(name="bufflike", description="Gửi lượt thích Free Fire tự động qua UID")
@app_commands.describe(uid="Nhập UID tài khoản người nhận", region="Khu vực (VN, SG, IND...)")
async def bufflike(interaction: discord.Interaction, uid: str, region: str):
    await interaction.response.defer(thinking=True)
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "uid": uid,
        "region": region.upper()
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "success":
            await interaction.followup.send(f"Đã gửi yêu cầu buff like thành công cho UID: `{uid}` (Khu vực: `{region}`).")
        else:
            error_message = data.get("message", "Lỗi không xác định từ máy chủ API.")
            await interaction.followup.send(f"Thực hiện thất bại: {error_message}")
    except Exception as e:
        await interaction.followup.send(f"Lỗi kết nối tới hệ thống API: {str(e)}")

# 3. KHỞI CHẠY SONG SONG WEB SERVER VÀ BOT
if __name__ == "__main__":
    keep_alive()
    client.run(DISCORD_TOKEN)

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1490072114089164920
guild = discord.Object(id=GUILD_ID)

FILE_NAME = "stock.json"

# تحميل المخزون
def load_stock():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# حفظ المخزون
def save_stock(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

stock = load_stock()

# تشغيل البوت
@bot.event
async def on_ready():

    # حذف الأوامر القديمة
    bot.tree.clear_commands(guild=guild)

    # مزامنة الأوامر الجديدة
    await bot.tree.sync(guild=guild)

    print(f"Logged in as {bot.user}")
    print("Slash commands synced!")

# ➕ إضافة مخزون
@bot.tree.command(
    name="add",
    description="إضافة سلاح للمخزون",
    guild=guild
)
@app_commands.describe(
    item="اسم السلاح",
    amount="الكمية"
)
async def add(interaction: discord.Interaction, item: str, amount: int):

    item = item.lower()

    if item in stock:
        stock[item] += amount
    else:
        stock[item] = amount

    save_stock(stock)

    await interaction.response.send_message(
        f"✅ تمت إضافة {amount} من {item}\n📦 الكمية الحالية: {stock[item]}"
    )

# ➖ خصم من المخزون
@bot.tree.command(
    name="neg",
    description="خصم كمية من المخزون",
    guild=guild
)
@app_commands.describe(
    item="اسم السلاح",
    amount="الكمية"
)
async def neg(interaction: discord.Interaction, item: str, amount: int):

    item = item.lower()

    if item not in stock:
        await interaction.response.send_message("❌ السلاح غير موجود")
        return

    if stock[item] < amount:
        await interaction.response.send_message("❌ الكمية غير كافية")
        return

    stock[item] -= amount

    save_stock(stock)

    await interaction.response.send_message(
        f"✅ تم خصم {amount} من {item}\n📦 المتبقي: {stock[item]}"
    )

# 💰 بيع مع سجل
@bot.tree.command(
    name="sell",
    description="بيع سلاح مع تسجيل العملية",
    guild=guild
)
@app_commands.describe(
    item="اسم السلاح",
    amount="الكمية",
    customer="اسم الزبون"
)
async def sell(
    interaction: discord.Interaction,
    item: str,
    amount: int,
    customer: str
):

    await interaction.response.defer()

    item = item.lower()

    if item not in stock:
        await interaction.followup.send("❌ السلاح غير موجود")
        return

    if stock[item] < amount:
        await interaction.followup.send("❌ الكمية غير كافية")
        return

    stock[item] -= amount

    save_stock(stock)

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    log_message = f"""
🧾 عملية بيع جديدة
━━━━━━━━━━━━━━
👤 الزبون: {customer}
🔫 السلاح: {item}
📦 الكمية: {amount}
🕒 الوقت: {time_now}
📉 المتبقي: {stock[item]}
━━━━━━━━━━━━━━
"""

    with open("sales_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_message + "\n")

    await interaction.followup.send(
        f"""✅ تمت عملية البيع

👤 الزبون: {customer}
🔫 السلاح: {item}
📦 الكمية: {amount}
📉 المتبقي: {stock[item]}"""
    )

# 📦 فحص سلاح
@bot.tree.command(
    name="check",
    description="فحص كمية سلاح",
    guild=guild
)
@app_commands.describe(
    item="اسم السلاح"
)
async def check(interaction: discord.Interaction, item: str):

    item = item.lower()

    if item not in stock:
        await interaction.response.send_message("❌ السلاح غير موجود")
        return

    await interaction.response.send_message(
        f"📦 المتوفر من {item}: {stock[item]}"
    )

# 📋 عرض جميع المخزون
@bot.tree.command(
    name="stockall",
    description="عرض جميع المخزون",
    guild=guild
)
async def stockall(interaction: discord.Interaction):

    if not stock:
        await interaction.response.send_message("📦 المخزون فارغ")
        return

    embed = discord.Embed(
        title="📋 جميع المخزون",
        color=0x00ff00
    )

    message = ""

    for item, amount in stock.items():
        message += f"🔫 **{item.upper()}** — `{amount}`\n"

    embed.description = message

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
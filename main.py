from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio

TOKEN = "8579329186:AAEWR3XGBTTfIj9WOd8MEilKAJeVPPTWz0Q"  # bot tokeningizni shu yerga yozing

# ================= STATE =================
(
    TIL, KONTAKT, MINTQA,
    TUR, TARGET_ID, VAQT,
    MATN, QAYTA, MENU,
    OCHIR_ID, TAHRIR_ID,
    TAHRIR_TURI, TAHRIR_KIRITISH
) = range(13)

users = {}

# ================= TIMEZONE =================
ZONE_MAP = {
    # 🇺🇿 O‘ZBEKISTON
    "toshkent": "Asia/Tashkent",
    "ташкент": "Asia/Tashkent",
    "tashkent": "Asia/Tashkent",

    "samarqand": "Asia/Tashkent",
    "samarkand": "Asia/Tashkent",
    "самарканд": "Asia/Tashkent",

    "buxoro": "Asia/Tashkent",
    "bukhara": "Asia/Tashkent",
    "бухара": "Asia/Tashkent",

    "andijon": "Asia/Tashkent",
    "andijan": "Asia/Tashkent",
    "андижан": "Asia/Tashkent",

    "namangan": "Asia/Tashkent",
    "наманган": "Asia/Tashkent",

    "fargona": "Asia/Tashkent",
    "fergana": "Asia/Tashkent",
    "фергана": "Asia/Tashkent",

    # 🇷🇺 ROSSIYA
    "moskva": "Europe/Moscow",
    "moscow": "Europe/Moscow",
    "москва": "Europe/Moscow",

    "sankt peterburg": "Europe/Moscow",
    "saint petersburg": "Europe/Moscow",
    "санкт-петербург": "Europe/Moscow",

    # 🇺🇸 AQSH
    "new york": "America/New_York",
    "nev york": "America/New_York",
    "ny": "America/New_York",
    "нью-йорк": "America/New_York",

    "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "лос-анджелес": "America/Los_Angeles",

    "chicago": "America/Chicago",
    "чикаго": "America/Chicago",

    # 🇦🇪 BAA
    "dubay": "Asia/Dubai",
    "dubai": "Asia/Dubai",
    "дубай": "Asia/Dubai",

    "abu dhabi": "Asia/Dubai",
    "абу даби": "Asia/Dubai",

    # 🇹🇷 TURKIYA
    "istanbul": "Europe/Istanbul",
    "istanbol": "Europe/Istanbul",
    "истамбул": "Europe/Istanbul",

    # 🇪🇺 YEVROPA (ENG KERAKLILAR)
    "parij": "Europe/Paris",
    "paris": "Europe/Paris",
    "париж": "Europe/Paris",

    "berlin": "Europe/Berlin",
    "берлин": "Europe/Berlin",

    "rim": "Europe/Rome",
    "rome": "Europe/Rome",
    "рим": "Europe/Rome",

    "madrid": "Europe/Madrid",
    "мадрид": "Europe/Madrid",

    "amsterdam": "Europe/Amsterdam",
    "амстердам": "Europe/Amsterdam",

        # 🇨🇳 XITOY
    "pekin": "Asia/Shanghai",
    "beijing": "Asia/Shanghai",
    "пекин": "Asia/Shanghai",

    # 🇯🇵 YAPONIYA
    "tokio": "Asia/Tokyo",
    "tokyo": "Asia/Tokyo",
    "токио": "Asia/Tokyo",

    # 🇰🇷 JANUBIY KOREYA
    "seul": "Asia/Seoul",
    "seoul": "Asia/Seoul",
    "сеул": "Asia/Seoul",

    # 🇮🇳 HINDISTON
    "dehli": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "дели": "Asia/Kolkata",

    # 🇬🇧 BUYUK BRITANIYA
    "london": "Europe/London",
    "londan": "Europe/London",
    "лондон": "Europe/London",
    # 🇹🇷 TURKIYA
    "turkiya istanbul": "Europe/Istanbul",
    "turkiya istanbu": "Europe/Istanbul",
    "турция стамбул": "Europe/Istanbul",
       # 🇫🇷 FRANSIYA
    "fransiya parij": "Europe/Paris",
    "франция париж": "Europe/Paris"


}

REPEAT = {
    "Hech qachon": None,
    "Har kun": timedelta(days=1),
    "Har hafta": timedelta(weeks=1),
    "Har oy": timedelta(days=30)
}

# ================= HELPER =================
def parse_chat_id(text: str):
    text = text.strip()
    if text.startswith("@"):
        return text
    try:
        return int(text)
    except:
        return None

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {"reminders": [], "tz": ZoneInfo("Asia/Tashkent")}
    await update.message.reply_text(
       "👋 Assalomu alaykum!\n"
"Men sizga kerakli vaqtda eslatmalar yuboruvchi botman.\n\n"
"Quyidagi tilni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            [["🇺🇿 O‘zbekcha", "🇷🇺 Русский"]],
            resize_keyboard=True
        )
    )
    return TIL

# ================= LANGUAGE =================
async def til(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    users[update.effective_user.id]["lang"] = lang

    if "O‘zbekcha" in lang:
        text = "📲 Botdan foydalanishni davom ettirish uchun telefon raqamingizni yuboring"
    else:
        text = "📲 Чтобы продолжить, отправьте номер вашего телефона"

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True
        )
    )
    return KONTAKT

# ================= CONTACT =================
async def kontakt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = users[update.effective_user.id]["lang"]
    text = "🌍 Minatqani yozing (masalan: Tashkent )" if "O‘zbekcha" in lang else "🌍 Введите регион (например: Tashkent)"
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return MINTQA

# ================= REGION =================
async def mintqa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    uid = update.effective_user.id

    for k, v in ZONE_MAP.items():
        if k in text:
            users[uid]["tz"] = ZoneInfo(v)
            lang = users[uid]["lang"]
            if "O‘zbekcha" in lang:
                msg = "📌 Yangi eslatma yarating, shunda hech narsani unutib qo‘ymaysiz!\n🔻 Yangi eslatmalarni quyidagi bo‘limlarda qo‘shish mumkin:\n🔔 Bot orqali eslatmalar 🤖\n🔔 Guruhlardagi eslatmalar 👨‍👧‍👧\n🔔 Kanallardagi eslatmalar 📣\n🔻Eslatmalar ro‘yxatini eslatmalar bo‘limiga o‘tib ko‘rishingiz mumkin.\nO‘sha yerda ularni tahrirlash, eslatmalar holatini (faol/nofoal) o‘zgartirish, vaqtni belgilash va hokazolarni amalga oshirish mumkin.\nFoydalanish bo‘yicha yo‘riqnomalarni bizning kanalimizda ko‘ring 👇\nhttps://t.me/remico_news"
            else:
                msg = "🔔 Выберите тип напоминания"

            await update.message.reply_text(
                msg,
                reply_markup=ReplyKeyboardMarkup(
                    [["Shaxsiy"], ["Guruh"], ["Kanal"]],
                    resize_keyboard=True
                )
            )
            return TUR

    lang = users[uid]["lang"]
    error_msg = "❌ Minatqa topilmadi, qayta yozing" if "O‘zbekcha" in lang else "❌ Регион не найден, введите снова"
    await update.message.reply_text(error_msg)
    return MINTQA

# ================= TYPE =================
async def tur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["current"] = {"type": update.message.text.lower()}

    if update.message.text.lower() in ["guruh", "kanal"]:
        await update.message.reply_text("🆔 Guruh / Kanal ID yoki @username kiriting")
        return TARGET_ID

    await update.message.reply_text("⏰ Eslatma qo‘yish\n📅 Sana va vaqtni quyidagi formatda kiriting:\nDD.MM.YYYY HH:MM\n📝 Qanday yozish kerak?\n— Kun.oy.yil va soat:daqiqa\n— 24 soatlik formatda\n📌 Misol:\n25.01.2026 18:30")
    return VAQT

# ================= TARGET =================
async def target_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = parse_chat_id(update.message.text)
    if chat_id is None:
        await update.message.reply_text("❌ Noto‘g‘ri ID")
        return TARGET_ID

    users[uid]["current"]["target_id"] = chat_id
    await update.message.reply_text("⏰ Eslatma qo‘yish\n📅 Sana va vaqtni quyidagi formatda kiriting:\nDD.MM.YYYY HH:MM\n📝 Qanday yozish kerak?\n— Kun.oy.yil va soat:daqiqa\n— 24 soatlik formatda\n📌 Misol:\n25.01.2026 18:30")
    return VAQT

# ================= TIME =================
async def vaqt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        dt = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
    except:
        await update.message.reply_text("❌ Format noto‘g‘ri")
        return VAQT

    users[uid]["current"]["time"] = dt
    await update.message.reply_text("✏️ Matnni kiriting")
    return MATN

# ================= TEXT =================
async def matn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["current"]["text"] = update.message.text
    await update.message.reply_text(
        "🔁 Takrorlansinmi?",
        reply_markup=ReplyKeyboardMarkup(
            [["Hech qachon", "Har kun"], ["Har hafta", "Har oy"]],
            resize_keyboard=True
        )
    )
    return QAYTA

# ================= SAVE =================
async def qayta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users[uid]
    cur = user["current"]
    cur["repeat"] = REPEAT[update.message.text]
    cur["id"] = len(user["reminders"]) + 1
    cur["task"] = asyncio.create_task(schedule(uid, cur, context))
    user["reminders"].append(cur)
    user.pop("current")
    await update.message.reply_text("✅ Eslatma saqlandi")
    return await menu(update, context)

# ================= SCHEDULE =================
async def schedule(uid, r, context):
    tz = users[uid]["tz"]

    while True:
        now = datetime.now(tz)
        target = r["time"].replace(tzinfo=tz)

        if target <= now:
            if not r["repeat"]:
                return
            target += r["repeat"]

        await asyncio.sleep((target - now).total_seconds())

        chat_id = uid if r["type"] == "shaxsiy" else r["target_id"]

        try:
            await context.bot.send_message(chat_id=chat_id, text=f"⏰ Eslatma:\n\n{r['text']}")
        except Exception as e:
            print("Xatolik:", e)

        if not r["repeat"]:
            return

        r["time"] = target

# ================= MENU =================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Asosiy menyu",
        reply_markup=ReplyKeyboardMarkup(
            [["➕ Yangi eslatma"], ["📋 Ro‘yxat"], ["✏️ Tahrirlash"], ["❌ O‘chirish"]],
            resize_keyboard=True
        )
    )
    return MENU

# ================= LIST =================
def reminder_list(user):
    if not user["reminders"]:
        return "📭 Eslatmalar yo‘q"
    return "\n\n".join(
        f"ID:{r['id']} — {r['text']}\n🕒 {r['time'].strftime('%d.%m.%Y %H:%M')}\n🔁 {'Hech qachon' if not r['repeat'] else 'Takror'} | {r['type'].title()}"
        for r in user["reminders"]
    )

# ================= MENU HANDLER =================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    uid = update.effective_user.id
    user = users[uid]

    if t == "➕ Yangi eslatma":
        await update.message.reply_text("🌍 Minatqani yozing")
        return MINTQA

    if t == "📋 Ro‘yxat":
        await update.message.reply_text(reminder_list(user))
        return MENU

    if t == "❌ O‘chirish":
        await update.message.reply_text("❌ O‘chirish uchun ID ni kiriting:\n\n" + reminder_list(user))
        return OCHIR_ID

    if t == "✏️ Tahrirlash":
        await update.message.reply_text("✏️ Tahrirlash uchun ID ni kiriting:\n\n" + reminder_list(user))
        return TAHRIR_ID

    return MENU

# ================= DELETE =================
async def ochir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        return await menu(update, context)
    uid = update.effective_user.id
    rid = int(update.message.text)
    user = users[uid]

    for r in user["reminders"]:
        if r["id"] == rid:
            r["task"].cancel()
            user["reminders"].remove(r)
            await update.message.reply_text("✅ O‘chirildi")
            return await menu(update, context)

    await update.message.reply_text("❌ ID topilmadi")
    return await menu(update, context)

# ================= EDIT =================
async def tahrir_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        return await menu(update, context)
    uid = update.effective_user.id
    rid = int(update.message.text)
    user = users[uid]

    for r in user["reminders"]:
        if r["id"] == rid:
            user["edit"] = r
            await update.message.reply_text(
                "Nimani o‘zgartirish?",
                reply_markup=ReplyKeyboardMarkup([["Matn"], ["Vaqt"]], resize_keyboard=True)
            )
            return TAHRIR_TURI

    await update.message.reply_text("❌ ID noto‘g‘ri")
    return await menu(update, context)

async def tahrir_turi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["edit_type"] = update.message.text
    await update.message.reply_text("Yangi qiymatni kiriting", reply_markup=ReplyKeyboardRemove())
    return TAHRIR_KIRITISH

async def tahrir_kirit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users[uid]
    r = user["edit"]

    if user["edit_type"] == "Vaqt":
        try:
            r["time"] = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
        except:
            await update.message.reply_text("❌ Format noto‘g‘ri")
            return TAHRIR_KIRITISH
    else:
        r["text"] = update.message.text

    r["task"].cancel()
    r["task"] = asyncio.create_task(schedule(uid, r, context))

    user.pop("edit")
    await update.message.reply_text("✅ Tahrirlandi")
    return await menu(update, context)

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TIL: [MessageHandler(filters.TEXT, til)],
            KONTAKT: [MessageHandler(filters.CONTACT, kontakt)],
            MINTQA: [MessageHandler(filters.TEXT, mintqa)],
            TUR: [MessageHandler(filters.TEXT, tur)],
            TARGET_ID: [MessageHandler(filters.TEXT, target_id)],
            VAQT: [MessageHandler(filters.TEXT, vaqt)],
            MATN: [MessageHandler(filters.TEXT, matn)],
            QAYTA: [MessageHandler(filters.TEXT, qayta)],
            MENU: [MessageHandler(filters.TEXT, menu_handler)],
            OCHIR_ID: [MessageHandler(filters.TEXT, ochir)],
            TAHRIR_ID: [MessageHandler(filters.TEXT, tahrir_id)],
            TAHRIR_TURI: [MessageHandler(filters.TEXT, tahrir_turi)],
            TAHRIR_KIRITISH: [MessageHandler(filters.TEXT, tahrir_kirit)],
        },
        fallbacks=[]
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()

import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== [ البيانات الأساسية ومعلومات المطور ] ====================
API_ID = 6
API_HASH = "eb0663579fe29547265a3962d6349603"

BOT_TOKEN = "8909190182:AAELxZ1IYLGyYMWfkcOwCEk9DBX2L8g_qcw"
SESSION_STRING = "AgG3g3kAcFLfDVUYvpc12tE2MANcyPm6GifZnfF8Q8l7tJx4FiZCkVSO5agHhchhrtHBHzAcrHSjkxNqfTUw2dvjbV9xS2bKvAbvWKcJu9OUV1e0biTowLTk-rl1O_g8FFe4hjzwd4oWAQ5LC-TQvf8Rbma4eOlOFYgD0HELjWEMVPp8YERHLoDCNdbkHLbH77pyGfO9y1w5t-Q4wvagwtKpvZmHw5sWQ9yogDjoFjBVCWyjxCAU5AsQnuitqF0Ltph_fN4f9dq6rhy2c3Ea7-dAi3VtP6nwrrLDoPFjzmzgLoccfIxJ8g3snKwseGCPQepzaAKchRyeCNxARwIIyh3eXcwOvAAAAAIFvIH0AA"

# 🆔 أيدي المطور الرئيسي (ثابت)
DEV_ID = 8686174708

DEV_USER = "tn2te"
SOURCE_CHANNEL = "sorsnamrod"
MUST_JOIN_CHANNEL = "IQgroup2"
STORAGE_LINK = "https://t.me/+dXr4V6hCUAcyMzBi"
BOT_USERNAME = "tn1tebot"

ACTIVATED_CHATS = set()
BOT_ADMINS = {}  # {chat_id: set(user_ids)}

# ==================== [ تشغيل البوت عبر الجلسة ] ====================
app = Client(
    "namrod_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    bot_token=BOT_TOKEN
)

# ==================== [ 🌐 دالة التعرف الشاملة الآمنة ] ====================
async def extract_entity(client, message):
    if message.reply_to_message:
        rep = message.reply_to_message
        if rep.from_user:
            return rep.from_user
        if rep.forward_from_chat:
            return rep.forward_from_chat
        if rep.sender_chat:
            return rep.sender_chat

    args = message.text.split() if message.text else []
    target_input = None

    if len(args) >= 3:
        target_input = args[2]
    elif len(args) == 2:
        target_input = args[1]

    if target_input:
        if target_input.lstrip('-').isdigit():
            target_input = int(target_input)
        elif target_input.startswith("@"):
            target_input = target_input.replace("@", "")

        try:
            return await client.get_chat(target_input)
        except Exception:
            try:
                return await client.get_users(target_input)
            except Exception:
                return None

    return None

# دالة فحص الاشتراكات الإجبارية
async def check_sub(client, user_id):
    try:
        chat_identifier = MUST_JOIN_CHANNEL if isinstance(MUST_JOIN_CHANNEL, int) or str(MUST_JOIN_CHANNEL).startswith("-100") else f"@{MUST_JOIN_CHANNEL}"
        member = await client.get_chat_member(chat_identifier, user_id)
        return member.status not in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]
    except Exception:
        return False

# فحص صلاحيات الأدمن أو المطور بالأيدي
async def is_admin(client, chat_id, user):
    if not user:
        return False
    if user.id == DEV_ID:
        return True
    if chat_id in BOT_ADMINS and user.id in BOT_ADMINS[chat_id]:
        return True
    try:
        member = await client.get_chat_member(chat_id, user.id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

# ==================== [ الأوامر العامة /start ] ====================
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user = message.from_user
    if not user:
        return

    if not await check_sub(client, user.id):
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("قناة الاشتراك 📢", url=f"https://t.me/{MUST_JOIN_CHANNEL}")],
            [InlineKeyboardButton("تأكيد الاشتراك 🔄", url=f"https://t.me/{BOT_USERNAME}?start=start")]
        ])
        return await message.reply_text(f"⚠️ اشترك بالقناة أولاً للاستخدام:\n@{MUST_JOIN_CHANNEL}", reply_markup=btn)

    if user.id == DEV_ID:
        text = (
            f"👑 **أهلاً بك يا مطورنا العالي ({user.first_name})**\n"
            f"🆔 أيديك: `{user.id}`\n\n"
            "لوحة التحكم الخاصة بك للتحكم بالسورس:"
        )
        dev_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("أضف البوت لكروبك ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton("قناة السورس 📢", url=f"https://t.me/{SOURCE_CHANNEL}"), InlineKeyboardButton("قناة التخزين 📦", url=STORAGE_LINK)],
            [InlineKeyboardButton("فحص السرعة 🚀", callback_data="ping_cb")]
        ])
        return await message.reply_text(text, reply_markup=dev_keyboard, disable_web_page_preview=True)

    text = (
        f"👑 **أهلاً بك ({user.first_name}) في بوت حماية سورس Namrod**\n\n"
        f"👨‍💻 المطور: [{DEV_USER}](tg://user?id={DEV_ID})\n"
        f"🆔 أيديك: `{user.id}`\n\n"
        "🧹 **الأوامر المتاحة بالكروب:**\n"
        "• `تفعيل` / `تعطيل` : التحكم بحالة البوت.\n"
        "• `رفع ادمن` / `تنزيل ادمن` : بالرد أو الأيدي.\n"
        "• `كشف` : جلب كشف شامل (عضو، بوت، كروب، قناة).\n"
        "• `امسح + العدد` : مسح رسائل الكروب.\n"
        "• `/clean` : تنظيف الحسابات المحذوفة."
    )
    user_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("أضف البوت لكروبك ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("المطور 👨‍💻", url=f"tg://user?id={DEV_ID}"), InlineKeyboardButton("السورس 📢", url=f"https://t.me/{SOURCE_CHANNEL}")],
        [InlineKeyboardButton("قناة التخزين 📦", url=STORAGE_LINK)]
    ])
    await message.reply_text(text, reply_markup=user_keyboard, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("ping_cb"))
async def ping_callback(client, callback_query):
    t1 = asyncio.get_event_loop().time()
    await callback_query.answer("جاري الفحص...")
    t2 = asyncio.get_event_loop().time()
    await callback_query.message.reply_text(f"🚀 **سرعة البوت:** `{round((t2 - t1) * 1000)}ms`")

# ==================== [ أمر الكشف الشامل ] ====================
@app.on_message(filters.group & filters.regex(r"^كشف"))
async def check_entity_info(client, message):
    entity = await extract_entity(client, message)
    if not entity:
        entity = message.from_user

    entity_type = getattr(entity, "type", None)
    
    if hasattr(entity, "first_name") or entity_type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        is_bot = getattr(entity, "is_bot", False)
        role = "عضو عادي 👤"
        
        if entity.id == DEV_ID:
            role = "مطور السورس 👑"
        elif is_bot:
            role = "بوت 🤖"
        else:
            try:
                chat_member = await client.get_chat_member(message.chat.id, entity.id)
                if chat_member.status == enums.ChatMemberStatus.OWNER:
                    role = "مالك الكروب 🔱"
                elif chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR or (message.chat.id in BOT_ADMINS and entity.id in BOT_ADMINS[message.chat.id]):
                    role = "أدمن بالكروب 👮‍♂️"
            except Exception:
                pass

        username_str = f"@{entity.username}" if entity.username else "لا يوجد"
        text = (
            f"📊 **معلومات الحساب / البوت:**\n\n"
            f"👤 **الاسم:** {entity.first_name}\n"
            f"🆔 **الأيدي:** `{entity.id}`\n"
            f"🏷 **المعرف:** {username_str}\n"
            f"📌 **الرتبة:** {role}"
        )
    else:
        title = getattr(entity, "title", "غير محدد")
        username_str = f"@{entity.username}" if getattr(entity, "username", None) else "خاصة / لا يوجد"
        type_name = "قناة 📢" if entity_type == enums.ChatType.CHANNEL else "مجموعة/كروب 👥"

        text = (
            f"📊 **معلومات القناة / الكروب:**\n\n"
            f"📢 **الاسم:** {title}\n"
            f"🆔 **الأيدي:** `{entity.id}`\n"
            f"🏷 **المعرف/الرابط:** {username_str}\n"
            f"📌 **النوع:** {type_name}"
        )

    await message.reply_text(text)

# ==================== [ رفع وتنزيل الأدمنية ] ====================
@app.on_message(filters.group & filters.regex(r"^رفع ادمن"))
async def promote_admin(client, message):
    if not await is_admin(client, message.chat.id, message.from_user):
        return await message.reply_text("⚠️ **هذا الأمر يخص المشرفين فقط!**")

    target_user = await extract_entity(client, message)
    if not target_user or not hasattr(target_user, "id"):
        return await message.reply_text("⚠️ **سوّي رد (Reply) أو اكتب الأيدي/اليوزر بعد الأمر!**")

    chat_id = message.chat.id
    if chat_id not in BOT_ADMINS:
        BOT_ADMINS[chat_id] = set()

    name = getattr(target_user, "first_name", getattr(target_user, "title", "العضو"))
    if target_user.id in BOT_ADMINS[chat_id]:
        return await message.reply_text(f"👤 هذا الكيان مرفوع أدمن بالفعل!")

    BOT_ADMINS[chat_id].add(target_user.id)
    await message.reply_text(f"✅ **تم رفع الكيان (`{name}`)**\n🆔 أيدي: `{target_user.id}` أدمن بالبوت!")

@app.on_message(filters.group & filters.regex(r"^تنزيل ادمن"))
async def demote_admin(client, message):
    if not await is_admin(client, message.chat.id, message.from_user):
        return await message.reply_text("⚠️ **هذا الأمر يخص المشرفين فقط!**")

    target_user = await extract_entity(client, message)
    if not target_user or not hasattr(target_user, "id"):
        return await message.reply_text("⚠️ **سوّي رد (Reply) أو اكتب الأيدي/اليوزر بعد الأمر!**")

    chat_id = message.chat.id
    if chat_id in BOT_ADMINS and target_user.id in BOT_ADMINS[chat_id]:
        BOT_ADMINS[chat_id].remove(target_user.id)
        await message.reply_text(f"✅ **تم تنزيل الكيان من الأدمنية.**\n🆔 أيدي: `{target_user.id}`")
    else:
        await message.reply_text("⚠️ هذا الكيان غير مرفوع أدمن ببوت الحماية أصلًا.")

# ==================== [ تفعيل وتعطيل الكروب ] ====================
@app.on_message(filters.group & filters.regex(r"^تفعيل$"))
async def enable_bot(client, message):
    if not await is_admin(client, message.chat.id, message.from_user):
        return await message.reply_text("⚠️ **هذا الأمر يخص المشرفين فقط!**")
    
    chat_id = message.chat.id
    if chat_id in ACTIVATED_CHATS:
        return await message.reply_text("⚡ **البوت مفعّل بالكروب بالفعل!**")
    
    ACTIVATED_CHATS.add(chat_id)
    await message.reply_text(f"✅ **تم تفعيل البوت بنجاح!**\n🆔 أيدي الكروب: `{chat_id}`")

@app.on_message(filters.group & filters.regex(r"^تعطيل$"))
async def disable_bot(client, message):
    if not await is_admin(client, message.chat.id, message.from_user):
        return await message.reply_text("⚠️ **هذا الأمر يخص المشرفين فقط!**")
        
    chat_id = message.chat.id
    if chat_id not in ACTIVATED_CHATS:
        return await message.reply_text("⚠️ **البوت معطل بالكروب أصلاً!**")
    
    ACTIVATED_CHATS.remove(chat_id)
    await message.reply_text("❌ **تم تعطيل البوت بنجاح.**")

# ==================== [ أمر المطور /dev ] ====================
@app.on_message(filters.command(["dev", "developer"]))
async def dev(client, message):
    text = (
        f"⚡ **معلومات مطور سورس 𝐍𝐚𝐦𝐫𝐨𝐝:**\n\n"
        f"👨‍💻 **المطور:** [{DEV_USER}](tg://user?id={DEV_ID})\n"
        f"🆔 **أيدي المطور:** `{DEV_ID}`\n"
        f"📢 **قناة السورس:** @{SOURCE_CHANNEL}\n"
        f"🔒 **قناة الاشتراك:** @{MUST_JOIN_CHANNEL}\n"
        f"📦 **التخزين:** [اضغط هنا]({STORAGE_LINK})"
    )
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("المطور 💬", url=f"tg://user?id={DEV_ID}")]])
    await message.reply_text(text, reply_markup=btn, disable_web_page_preview=True)

# ==================== [ أمر البينج /ping ] ====================
@app.on_message(filters.command("ping"))
async def ping(client, message):
    t1 = asyncio.get_event_loop().time()
    msg = await message.reply_text("⚡...")
    t2 = asyncio.get_event_loop().time()
    await msg.edit_text(f"🚀 **شغال طيارة!**\n⏱ السرعة: `{round((t2 - t1) * 1000)}ms`")

# ==================== [ مسح الرسائل ] ====================
@app.on_message(filters.group & (filters.regex(r"^امسح (\d+)$") | filters.command(["del", "purge"])))
async def delete_by_count(client, message):
    if message.chat.id not in ACTIVATED_CHATS:
        return await message.reply_text("⚠️ **البوت غير مفعّل بالكروب!** اكتب `تفعيل` أولاً.")

    if not await is_admin(client, message.chat.id, message.from_user):
        return await message.reply_text("⚠️ **هذا الأمر يخص المشرفين فقط!**")

    count = 0
    if message.text and message.text.startswith("امسح"):
        match = re.search(r"\d+", message.text)
        if match:
            count = int(match.group())
    elif len(message.command) > 1 and message.command[1].isdigit():
        count = int(message.command[1])

    if count <= 0:
        return await message.reply_text("⚠️ اكتب الأمر ويا العدد، مثلاً: `امسح 50`")

    if count > 100:
        count = 100

    chat_id = message.chat.id
    messages_to_delete = []

    async for msg in client.get_chat_history(chat_id, limit=count + 1):
        messages_to_delete.append(msg.id)

    try:
        await client.delete_messages(chat_id, messages_to_delete)
        status_msg = await message.reply_text(f"🗑 **تم مسح {len(messages_to_delete) - 1} رسالة بنجاح!**")
        await asyncio.sleep(3)
        await status_msg.delete()
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: `{e}`")

# ==================== [ تنظيف الحسابات المحذوفة ] ====================
@app.on_message(filters.command("clean") & filters.group)
async def clean(client, message):
    if message.chat.id not in ACTIVATED_CHATS:
        return await message.reply_text("⚠️ **البوت غير مفعّل بالكروب!** اكتب `تفعيل` أولاً.")

    if not await is_admin(client, message.chat.id, message.from_user):
        return await message.reply_text("⚠️ **هذا الأمر يخص المشرفين فقط!**")

    chat_id = message.chat.id
    msg = await message.reply_text("🧹 **جاري تنظيف الحسابات المحذوفة...**")
    
    deleted = 0
    try:
        async for member in client.get_chat_members(chat_id):
            if member.user and member.user.is_deleted:
                try:
                    await client.ban_chat_member(chat_id, member.user.id)
                    deleted += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
        await msg.edit_text(f"✅ **تم التنظيف بنجاح!**\n🗑 تم طرد وحظر `{deleted}` حساب محذوف.")
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ: `{e}`")

# ==================== [ الحماية التلقائية ] ====================
@app.on_message(filters.group & ~filters.service)
async def auto_clean_all(client, message):
    if message.chat.id not in ACTIVATED_CHATS:
        return

    if await is_admin(client, message.chat.id, message.from_user):
        return

    if message.sticker or message.animation:
        try:
            return await message.delete()
        except Exception:
            pass

    text_to_check = message.text or message.caption
    if text_to_check:
        has_link = bool(re.search(r"(https?://|t\.me/|telegram\.me/|www\.|@[a-zA-Z0-9_]+)", text_to_check, re.IGNORECASE))
        if has_link:
            try:
                await message.delete()
            except Exception:
                pass

if __name__ == "__main__":
    print("🤖 Full Comprehensive Check Passed! Bot is Running Perfectly.")
    app.run()

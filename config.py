import os

botRoot = os.path.dirname(os.path.realpath(__file__))
commands = []
inlines = []
buttons = []

# Telegram Bot Token
token = ""
# 机器人的代理
proxy_url = None  # http://127.0.0.1:10809/
# get, post 的代理
proxies = {
    # "http://": f"http://127.0.0.1:10809/",
    # "https://": f"http://127.0.0.1:10809/"
}

# 使用自建 API 服务器，可提高文件上传下载大小限制
# 可参考教程 https://www.kuku.me/archives/41/
# docker: https://hub.docker.com/r/aiogram/telegram-bot-api/tags
base_url = 'https://api.telegram.org/bot' # http://0.0.0.0:8081/bot
base_file_url = 'https://api.telegram.org/file/bot' # http://0.0.0.0:8081/file/bot

pixiv_headers = {
  # Pixiv 的 Cookie, 只需要 PHPSESSID 字段
  "cookie": "PHPSESSID=",
}

twitter_headers = {
    'content-type': 'application/json; charset=utf-8',
    # Twitter 的 authorization
    'authorization': '',
    # Twitter 的 x-csrf-token
    'x-csrf-token': '',
    # Twitter 的 cookie
    'cookie': '',
    'X-Twitter-Client-Language': 'zh-cn',
    'X-Twitter-Active-User': 'yes'
}

ex_headers = {
  # exhentai 的 cookie, 只需要 ipb_member_id, ipb_pass_hash, igneous 字段
  "cookie": "ipb_member_id=; ipb_pass_hash=; igneous="
}

fanbox_headers = {
    # Fanbox 的 Cookie, 只需要 FANBOXSESSID 字段
    "cookie": "FANBOXSESSID=",
}

echo_chat_id = 0

bili_headers = {
  # cookie, 只需要 SESSDATA 字段
  'cookie': 'SESSDATA='
}
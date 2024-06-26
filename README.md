# tgbot
一个Telegram机器人，可以解析pixiv.net, x.com, e-hentai.org, exhentai.org, kemono.su等

demo: [@hbcao1bot](https://t.me/hbcao1bot)

## 特别说明

如果你在GitCode (https://gitcode.com) 看到本仓库，那么请点击该网站右侧简介下的GitHub徽标访问正确的GitHub仓库。因为GitCode上的仓库是由第三方在未经授权的情况下非法创建的，他们很有可能在其中植入病毒，从而感染你的计算机，并且可能会威胁到财产安全。如果该平台要求你输大电话号码或者什么密码以完成什么操作，那么千万不要输大，这很有可能会导致你的资金被盗。


## 安装 Installation
```
1.安装Python>=3.9

2.执行以下操作

```bash
# 1.克隆仓库或者手动下载
git clone https://github.com/HBcao233/tgbot
# 2.安装依赖
cd tgbot
pip install -r requirements.txt
```

3.（可选, 用于生成Twitter预览图）安装 google-chrome 或 chromium

```bash
# Ubantu
apt install https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# Centos
rpm -ivh https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
# 查看版本
google-chrome --version
```


## 配置 Configuration Bot
重命名 `.env.example` 为 `.env`，按照其中的注释修改配置

Rename `.env.example` to `.env`, and edit it by notes

token 必填，获取方法自行搜索 Telegram Bot Token

## 运行 How To Run
```
# 添加运行权限
chmod 755 tgbot.sh
# 启动bot
tgbot.sh start
# （可选）建立快捷方式
sudo ln -s path/to/mybot/tgbot.sh /usr/bin/mybot
# 查看运行状态
mybot status
# 查看运行日志
mybot log
# 关闭 bot
mybot stop
```

## 依赖 Dependencies
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [httpx](https://github.com/encode/httpx)
* [python-dotenv](https://github.com/theskumar/python-dotenv)
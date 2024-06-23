import traceback
from telegram import (
  Update,
  InlineKeyboardButton,
  InlineKeyboardMarkup,
  InlineQueryResultPhoto,
  InlineQueryResultsButton,
  InputMediaPhoto,
  InputMediaDocument,
)
import re
import os
import asyncio

import util
from util.log import logger
from util.progress import Progress
from plugin import handler, button_handler
from .data_source import headers, parsePidMsg, getAnime


_pattern = r'(?:^|^(?:pid|PID) ?|(?:https?://)?(?:www\.)?(?:pixiv\.net/(?:member_illust\.php\?.*illust_id=|artworks/|i/)))(\d{6,12})(?:[^0-9].*)?$'
@handler('pid', 
  private_pattern=_pattern,
  pattern=_pattern.replace(r'(?:^|', r'(?:'),
  info="获取p站作品 /pid <url/pid> [hide] [mark]"
)
async def _pixiv(update, context, text=None):
  if not (match := re.match(r'(?:pid|Pid|PID)? ?' +_pattern, text)):
    return await update.message.reply_text(
        "用法: /pid <url/pid> [hide/省略] [mark/遮罩] [origin/原图]\n"
        "url/pid: p站链接或pid\n"
        "[hide/省略]: 省略图片说明\n"
        "[mark/遮罩]: 给图片添加遮罩\n"
        "[origin/原图]: 发送原图\n"
        "私聊小派魔时可以省略/tid，直接发送<url/pid>哦\n"
        "或者使用@hbcao1bot <url/pid>作为内联模式发送~",
        reply_to_message_id=update.message.message_id,
    )
  pid = match.group(1)
    
  hide = False
  mark = False
  origin = False
  arr = text.split(" ")
  if "hide" in arr or '省略' in arr: 
    hide = True
  if "mark" in arr or '遮罩' in arr: 
    mark = True
  if 'origin' in arr or '原图' in arr: 
    origin = True
  logger.info(f"{pid = }, {hide = }, {mark = }, {origin = }")
  
  message = update.message
  bot = context.bot
  
  mid = await message.reply_text(
    "请等待...",
    reply_to_message_id=message.message_id,
  )
  try:
    url = f"https://www.pixiv.net/ajax/illust/{pid}"
    r = await util.get(url, headers=headers)
  except Exception:
    return await message.reply_text(
        "连接超时",
        reply_to_message_id=message.message_id,
    )
  res = r.json()
  if res["error"]:
    return await message.reply_text(
      '错误: ' + res["message"],
      reply_to_message_id=message.message_id,
    )
    
  res = res['body']
  msg = parsePidMsg(res, hide)
  if res['illustType'] == 2:
    await send_animation(update, context, pid, mid, origin)
  else:
    count = res["pageCount"]
    bar = Progress(
      bot, mid, total=count,
      prefix=f"正在获取 p1 ~ {count}",
    )
    if count < 11:
      try:
        await send_photos(update, context, bar, pid, res, origin, msg, mark)
      except Exception as e:
        logger.warning(traceback.format_exc())
        return await bot.edit_message_text(
          text=str(e),
          chat_id=message.chat.id,
          message_id=mid.message_id,
        )
        
      await bot.delete_message(
        chat_id=message.chat_id, message_id=mid.message_id
      )
    else:
      await send_telegraph(update, context, res, mid)
  
  if str(message.chat.type) != "private":
    return
  keyboard = [[
    InlineKeyboardButton(
      "获取原图" if not origin else '取消原图', 
      callback_data=(
        f"pid {pid}"
        f" {'hide' if hide else ''}"
        f" {'origin' if not origin else ''}"
      ),
    ),
    InlineKeyboardButton(
      "添加遮罩" if not mark else '取消遮罩', 
      callback_data=(
        f"pid {pid}"
        f" {'hide' if hide else ''}"
        f" {'mark' if not mark else ''}"
      ),
    ),
    InlineKeyboardButton(
      "详细描述" if hide else "简略描述", 
      callback_data=(
        f"pid {pid}"
        f" {'hide' if not hide else ''}"
        f" {'mark' if mark else ''}"
        f" {'origin' if origin else ''}"
      ),
    ),
  ]]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await message.reply_text(
    "获取完成", 
    reply_to_message_id=message.message_id,
    reply_markup=reply_markup,
  )
  
  
@button_handler(pattern=r"^pid \d{6,12}")
async def _(update, context, query):
  logger.info(update)
  message = update.callback_query.message
  _update = Update(
    update_id=update.update_id, 
    message=message, 
    callback_query=update.callback_query
  )
  await message.edit_reply_markup(reply_markup=None)
  await _pixiv(_update, context, query.data)
  
  
async def send_animation(update, context, pid, mid, origin):
  message = update.message
  bot = context.bot
  await update.message.reply_chat_action(action='upload_video')
  animations = util.Data('animations')
  if not (info := animations[pid]):
    anime = await getAnime(pid)
    if not anime:
      return await message.reply_text(
        '生成动图失败',
        reply_to_message_id=message.message_id,
      )
    info = util.videoInfo(anime)
  animation, duration, width, height, thumbnail = tuple(info)
  m = await message.reply_animation(
    animation=animation,
    duration=duration,
    width=width,
    height=height,
    thumbnail=thumbnail,
    caption=msg,
    parse_mode='HTML',
    has_spoiler=mark,
    reply_to_message_id=update.message.message_id,
  )
  v = m.animation
  animations[pid] = [v.file_id, v.duration, v.width, v.height, v.thumbnail.file_id]
  animations.save()
  await bot.delete_message(
    chat_id=message.chat.id, message_id=mid.message_id
  )
  
  
async def send_photos(update, context, bar, pid, res, origin, caption, mark):
  message = update.message
  bot = context.bot
  imgUrl = res["urls"]["regular"]
  if origin:
    imgUrl = res["urls"]["original"]
  count = res["pageCount"]
  data = util.Documents() if origin else util.Photos()
  
  async def get_img(i):
    nonlocal origin, data
    url = imgUrl.replace("_p0", f"_p{i}")
    name = f"{pid}_p{i}"
    if not origin:
      name += '_regular'
    if media := data[name]:
      return media
      
    try:
      img = await util.getImg(url, saveas=name, ext=True, headers=headers)
      if not origin:
        ext = os.path.splitext(img)[-1]
        img = util.resizePhoto(img)
        media = util.img2bytes(img, ext)
      else:
        media = open(img, 'rb')
    except Exception:
      logger.warning(traceback.format_exc())
      await update.message.reply_text(
        "图片获取失败",
        reply_to_message_id=message.message_id
      )
      raise Exception(f'p{i} 图片获取失败')
    
    bar.add(1)
    return media
  
  tasks = [get_img(i) for i in range(count)]
  result = await asyncio.gather(*tasks)
  ms = []
  t = InputMediaDocument if origin else InputMediaPhoto
  
  kwargs = {}
  if not origin:
    kwargs['has_spoiler'] = mark
  
  k = kwargs.copy()
  k.update({
    'media': result[0],
    'caption': caption, 
    'parse_mode': 'HTML',
  })
  ms.append(t(**k))
  for i in result[1:]:
    k = kwargs.copy()
    k['media'] = ai
    ms.append(t(**k))
    
  await update.message.reply_chat_action(action='upload_photo')
  
  try:
    m = await update.message.reply_media_group(
      media=ms,
      reply_to_message_id=update.message.message_id,
      read_timeout=120,
      write_timeout=120,
      connect_timeout=120,
      pool_timeout=120,
    )
    
    for i in range(count):
      name = f"{pid}_p{i}"
      if not origin:
        name += '_regular'
      tt = m[i].document if origin else m[i].photo[-1]
      data[name] = tt.file_id
    data.save()
  except Exception:
    raise Exception("发送失败")


async def send_telegraph(update, context, res):
  pass
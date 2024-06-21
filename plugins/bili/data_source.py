import asyncio
import httpx
from functools import cmp_to_key
import base64
import gzip
import struct

import util
import config
from util.log import logger
from .auth import getMixinKey, wbi


qn = 64


def _cmp(x, y):
  if x['id'] > qn:
    return 1
  if y['id'] > qn:
    return -1
  if x['id'] == y['id'] == qn:
    if x['codecid'] == 12:
      return -1
    if y['codecid'] == 12:
      return 1
    return 0
  if x['id'] < y['id']:
    return 1
  if x['id'] > y['id']:
    return -1
  return 0
  
  
async def getVideo(bvid, aid, cid):
  video_url = None
  audio_url = None
  videos, audios = await _get(aid, cid)
  if audios is None:
    video_url = videos
  else:
    # _videos = list(filter(lambda x: x['id']==qn, videos))
    videos = sorted(videos, key=cmp_to_key(_cmp))
    logger.info(f"qn: {videos[0]['id']}, codecid: {videos[0]['codecid']}")
    video_url = videos[0]['base_url']
    for i in audios:
      if i['id'] == 30216:
        audio_url = i['base_url']
        break
  
  result = await asyncio.gather(
    util.getImg(
      video_url,
      headers=dict(config.bili_headers, **{'Referer': 'https://www.bilibili.com'}),
    ), 
    util.getImg(
      audio_url,
      headers=dict(config.bili_headers, **{'Referer': 'https://www.bilibili.com'}),
    ),
  ) 
  path = util.getCache(f'{bvid}.mp4')
  command = ['ffmpeg', '-i', result[0]]
  if result[1] != '':
    command.extend(['-i', result[1]])
  command.extend(['-c:v', 'copy', '-c:a', 'copy', '-y', path])
  logger.info(f'{command = }')
  proc = await asyncio.create_subprocess_exec(
    *command,
    stdout=asyncio.subprocess.PIPE, 
    stdin=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
  )
  stdout, stderr = await proc.communicate()
  if proc.returncode != 0 and stderr: 
    logger.warning(stderr.decode('utf8'))
  
  return util.videoInfo(path)


async def _get(aid, cid):
  url = 'https://api.bilibili.com/x/player/wbi/playurl'
  mixin_key = await getMixinKey()
  params = {
    'fnver': 0,
    'fnval': 16,
    'qn': qn,
    'avid': aid,
    'cid': cid,
  }
  headers = {
    'Referer': 'https://www.bilibili.com',
  }
  r = await util.get(
    url,
    headers=dict(config.bili_headers, **headers),
    params=wbi(mixin_key, params),
  )
  logger.info(r.text)
  res = r.json()['data']
  if 'dash' in res:
    return res['dash']['video'], res['dash']['audio']
  return res['durl'][0]['url'], None
  
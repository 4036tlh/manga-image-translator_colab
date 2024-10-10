import os
import requests

import datetime
import random
import string
import time
from lxml import html

char_set = string.ascii_uppercase + string.digits


# fetch manga main page
def step_1(manga_url):  
  userAgentRandom = ''.join(random.sample(char_set*6, 6))
  manga_page_html = requests.get(manga_url, allow_redirects=True, headers = {'User-agent': userAgentRandom})
  manga_page_html = html.fromstring(manga_page_html.content)
  
  title        = manga_page_html.xpath('//h2[@class="manga-name"]/text()')
  title_or     = manga_page_html.xpath('//div[@class="manga-name-or"]/text()')
  description  = manga_page_html.xpath('//div[@class="description"]/text()')
  tags         = manga_page_html.xpath('//div[@class="genres"]/a//text()')
  ch_ids = manga_page_html.xpath('//ul[@id="ja-chaps"]/li/@data-id')
  ch_names  = manga_page_html.xpath('//ul[@id="ja-chaps"]/li/@data-number')

return title, title_or, description, tags, ch_url_ids[::-1], ch_names[::-1]

# fetch chapters' info
def step_2(ch_url_id):
  
  userAgentRandom = ''.join(random.sample(char_set*6, 6))
  temp = f'https://jmanga.org/json/chapter?mode=vertical&id={ch_url_id}'
  temp = requests.get(temp, allow_redirects=True, headers = {'User-agent': userAgentRandom})
  temp = html.fromstring(temp.json()['html'])
  temp = temp.xpath('//img/@data-src')

  ch_pages_number = len(temp)
  ch_id = temp[0].split('/')[-2]
  manga_id = temp[0].split('/')[-3]
  img_ext = temp[0].split('.')[-1]
  
  return manga_id, ch_id, ch_pages_number, img_ext

def download_image(img_url, tar_img_path):
  os.makedirs(os.path.dirname(tar_img_path), exist_ok=True)

  userAgentRandom = ''.join(random.sample(char_set*6, 6))
  img_data = requests.get(url=img_url, headers={'User-agent': userAgentRandom}).content
  with open(tar_img_path, 'wb', create_parents=True) as handler:
      handler.write(img_data)

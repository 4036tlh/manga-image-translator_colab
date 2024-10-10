import os
import requests

import datetime
import random
import string
import time
from lxml import html

import argparse

char_set = string.ascii_uppercase + string.digits

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help = "jmanga.org url")
parser.add_argument("-o", "--outputPath", help = "Output path")

args = parser.parse_args()

manga_url = args.outputPath
image_url_base = 'https://mgojp.mangadb.shop/files'

# fetch manga main page
userAgentRandom = ''.join(random.sample(char_set*6, 6))
manga_page_html = requests.get(manga_url, allow_redirects=True, headers = {'User-agent': userAgentRandom})
manga_page_html = html.fromstring(manga_page_html.content)

title        = manga_page_html.xpath('//h2[@class="manga-name"]/text()')
title_or     = manga_page_html.xpath('//div[@class="manga-name-or"]/text()')
description  = manga_page_html.xpath('//div[@class="description"]/text()')
chapter_list = manga_page_html.xpath('//ul[@id="ja-chaps"]/li/@data-id')
chapter_num  = manga_page_html.xpath('//ul[@id="ja-chaps"]/li/@data-number')

# fetch chapters' info
manga_id = 'E'
ch_pages_numbers = []
ch_ids = []
for idx, c in enumerate(chapter_list):
  temp = f'https://jmanga.org/json/chapter?mode=vertical&id={c}'
  temp = requests.get(temp, allow_redirects=True, headers = {'User-agent': userAgentRandom})
  temp = html.fromstring(temp.json()['html'])
  temp = temp.xpath('//img/@data-src')

  ch_pages_numbers.append(len(temp))
  ch_ids.append(temp[0].split('/')[-2])
  
  if idx == 0:   manga_id = temp[0].split('/')[-3]

#image_url = f'{image_url_base}/{manga_id}/{chapter_list[0]}/{page_No}.webp'

return manga_id, title, title_or, description, manga_id, chapter_num, ch_ids, ch_pages_numbers

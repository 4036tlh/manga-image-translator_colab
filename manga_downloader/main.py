from downloader import *

import argparse

char_set = string.ascii_uppercase + string.digits

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--DBPath", help = "DB path")
parser.add_argument("-u", "--url", help = "jmanga.org url")
parser.add_argument("-o", "--outputPath", help = "Output path")

args = parser.parse_args()

connection = sqlite3.connect(args.DBPath)
cursor = connection.cursor()

existed_manga_titles = cursor.execute("SELECT title FROM manga_main")

title, title_or, description, tags, ch_url_ids, ch_names = step_1(args.url)

new_ch = ''
new_ch_id = ''
new_page = ''
new_ext = ''

if title not in existed_manga_titles:
  for [ch_url_id, ch_name] in zip(ch_url_ids, ch_names):
    manga_id, ch_id, ch_pages_number, img_ext = step_2(ch_url_id)

    for i in range(ch_pages_number):
      img_url = f"https://mgojp.mangadb.shop/files/{manga_id}/{ch_id}/{i+1}.{img_ext}"
      tar_img_path = f"{args.outputPath}/{title}/{ch_name}/{i+1}.{img_ext}"
      download_image(img_url, tar_img_path)

    new_ch_name   = f"{new_ch_name},{ch_name}"
    new_ch_id     = f"{new_ch_id},{ch_id}"
    new_page      = f"{new_page},{ch_pages_number}"
    new_ext       = f"{new_ext},{img_ext}"
                        
  insert_query = f"INSERT INTO manga_main VALUES({manga_id},{title},{title_or},{description},{new_ch_name},{new_ch_id},{new_ext})"
  cursor.execute(insert_query)
else:
  existed_ch_name_list = cursor.execute(f"SELECT ch_name FROM manga_main where title={title}")
  existed_ch_name_list = existed_ch_name_list.split(',')
  
  if len(ch_names) != len(existed_ch_name_list):
    for [ch_url_id, ch_name in zip(ch_url_ids, ch_names):
      if ch_name not in existed_ch_name_list:
        manga_id, ch_id, ch_pages_number, img_ext = step_2(ch_url_id)
        
        for i in range(ch_pages_number):
          img_url = f"https://mgojp.mangadb.shop/files/{manga_id}/{ch_id}/{i+1}.{img_ext}"
          tar_img_path = f"{args.outputPath}/{title}/{ch_name}/{i+1}.{img_ext}"
          download_image(img_url, tar_img_path)

        new_ch_name   = f"{new_ch_name},{ch_name}"
        new_ch_id     = f"{new_ch_id},{ch_id}"
        new_page      = f"{new_page},{ch_pages_number}"
        new_ext       = f"{new_ext},{img_ext}"
        
    update_query = f"""
    UPDATE manga_main 
    SET ch_name = ch_name||', {new_ch_name}', 
    SET ch_id = ch_id||', {new_ch_id}',
    SET ext = ext||', {new_ext}'
    WHERE title={title}"""
    cursor.execute(update_query)
        




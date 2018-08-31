import logging
import os

import wget
from PIL import Image
from bs4 import BeautifulSoup

dir_to_store_image = '../../static/images'

logging.basicConfig(level=logging.INFO)


def download_emoji():
    with open('weibo_emoji.html', encoding='utf-8') as file:
        b = BeautifulSoup(file.read(), 'html.parser')
        lis_tag = b.find_all('li')
        if lis_tag:
            for li_tag in lis_tag:
                title = li_tag.get('title')
                url = 'http:' + li_tag.img.get('src')
                os.makedirs(dir_to_store_image, exist_ok=True)
                image_filename = url.split('/')[-1]
                wget.download(url, os.path.join(dir_to_store_image, image_filename))
                logging.info('Downloading ' + url)


def shrink_emoji():
    for image_filename in os.listdir(dir_to_store_image):
        logging.info('Resizing ' + image_filename)
        image_filename_with_path = os.path.join(dir_to_store_image, image_filename)
        Image.open(image_filename_with_path).resize((20, 20)).save(image_filename_with_path)


if __name__ == '__main__':
    download_emoji()
    shrink_emoji()

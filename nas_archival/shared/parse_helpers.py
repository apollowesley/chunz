import html
import os
import re
from datetime import datetime

import requests
from shared.constants import SINGLE_LINE_RE, EXTRACT_DT_RE, PARSE_IMAGE_LINK, PARSE_IMAGE_CAPTION, DEFAULT_TIMEOUT_SECS


def parse_cleanup(txt, dont_trim=False):
    clean = html.unescape(re.sub(SINGLE_LINE_RE, '', txt))

    return clean.strip() if not dont_trim else clean


def parse_extract_datetime(dt):
    return re.sub(EXTRACT_DT_RE, '\\1', dt)


def parse_clean_url(url):
    return re.sub(re.compile('/[?]+$'), '', url)


def parse_append_hostname(url):
    return 'https://www.mindef.gov.sg{}'.format(url) if url.startswith('/') else url


def parse_filename(dt):
    return datetime.strptime(dt, '%d %b %Y').strftime('%Y%m%d')


def parse_get_datetimestr(html):
    datetime_strs = html.xpath(
        '//div[@class="article-detail__heading"]/div[@class="article-info"]/span[contains(@class, "item-published")]/text()')

    return parse_extract_datetime(datetime_strs[0])


def parse_extract_img_link_caption(images):
    new_images = []

    for e in images:
        links = e.xpath('img/@src')
        link = links[0] if len(links) > 0 else ''
        link = parse_append_hostname(link)

        captions = e.xpath('span[@class="caption"]/text()')
        caption = captions[0] if len(captions) > 0 else ''
        caption = parse_cleanup(caption)

        new_images.append({
            PARSE_IMAGE_LINK: link,
            PARSE_IMAGE_CAPTION: caption,
        })

    return new_images


def parse_fetch_image(url, idx, filename_prefix, directory):
    image_filename = os.path.join(directory, '{}_IMG_{}.png'.format(filename_prefix, idx))
    image = requests.get(url, timeout=DEFAULT_TIMEOUT_SECS)

    with open(image_filename, 'wb') as f:
        f.write(image.content)

    return image_filename


def parse_is_invalid_content(page_content, status_code):
    return status_code != 200 or page_content is None or len(page_content) < 10 \
           or re.search(r'<title>File Not Found</title>', str(page_content)) is not None

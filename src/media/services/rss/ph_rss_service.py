from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, parse_qs

from lxml import etree
from requests import get

from src.media.models import VideoItem


class PhRssService:
    def read_rss(self):
        rss_url = "https://www.pornhub.com/video/webmasterss"
        response = get(rss_url)

        root = etree.fromstring(response.content)

        for item in root.xpath("//item"):
            dt = parsedate_to_datetime(item.findtext("pubDate"))
            parsed = urlparse(item.findtext("link"))
            external_id = parse_qs(parsed.query).get("viewkey", [None])[0]

            if VideoItem.objects.filter(external_id=external_id).exists():
                print(f'Video item already exists: {external_id}')
                continue

            VideoItem.objects.create(
                title=item.findtext("title"),
                link=item.findtext("link"),
                duration=item.findtext("duration"),
                thumb=item.findtext("thumb"),
                thumb_large=item.findtext("thumb_large"),
                embed_code=item.findtext("embed"),
                pub_date=dt,
                external_id=external_id,
                site='pornhub',
            )

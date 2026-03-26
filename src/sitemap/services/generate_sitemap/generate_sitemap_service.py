import gzip
import os

from django.utils import timezone

from automationapp import settings
from src.media.models import VideoItem
from src.sitemap.models import SitemapFile


class GenerateSitemapService():
    BATCH_SIZE = 50000  # Max URLs per sitemap

    def __init__(self):
        self.messages = []

    def generate_sitemap(self, full_regeneration: bool, use_gzip: bool) -> list:
        os.makedirs(settings.SITEMAPS_DIR, exist_ok=True)

        if full_regeneration:
            print("Performing full sitemap regeneration...")
            SitemapFile.objects.all().delete()  # reset metadata
            for f in os.listdir(settings.SITEMAPS_DIR):
                if f.startswith("sitemap_") and (f.endswith(".xml") or f.endswith(".xml.gz")):
                    os.remove(os.path.join(settings.SITEMAPS_DIR, f))
            next_start_id = 0
            next_index = 0
        else:
            last_sitemap = SitemapFile.objects.order_by('-end_id').first()
            if last_sitemap and last_sitemap.url_count < self.BATCH_SIZE:
                # Regenerate last partial sitemap
                next_start_id = last_sitemap.start_id
                next_index = int(last_sitemap.filename.split('_')[-1].split('.')[0])
                print(f"Regenerating partial sitemap: {last_sitemap.filename}")
                os.remove(os.path.join(settings.SITEMAPS_DIR, last_sitemap.filename))
                last_sitemap.delete()
            else:
                next_start_id = last_sitemap.end_id + 1 if last_sitemap else 0
                next_index = SitemapFile.objects.count()

        last_id = next_start_id

        while True:
            videos = list(VideoItem.objects.filter(id__gt=last_id).order_by('id')[:self.BATCH_SIZE])

            if not videos:
                break

            self.write_sitemap(videos, next_index, use_gzip)

            last_id = videos[-1].id
            next_index += 1

        # Generate sitemap index
        self.write_index()
        print("Sitemap generation complete.")

        return self.messages

    def write_sitemap(self, videos: list[VideoItem], index: int, use_gzip: bool):
        filename = f"sitemap_videos_{index}.xml"
        filepath = os.path.join(settings.SITEMAPS_DIR, filename)
        if use_gzip:
            filepath += ".gz"
            f = gzip.open(filepath, 'wt', encoding='utf-8')
        else:
            f = open(filepath, 'w', encoding='utf-8')

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for video in videos:
            f.write("  <url>\n")
            f.write(f"    <loc>{video.video_full_url}</loc>\n")
            f.write("  </url>\n")
        f.write("</urlset>\n")
        f.close()

        # Save metadata
        SitemapFile.objects.create(
            filename=os.path.basename(filepath),
            start_id=videos[0].id,
            end_id=videos[-1].id,
            url_count=len(videos)
        )
        message = f"Generated {os.path.basename(filepath)} with {len(videos)} URLs"
        self.messages.append(message)
        print(message)

    def write_index(self):
        index_path = os.path.join(settings.SITEMAPS_DIR, "sitemap.xml")
        f = open(index_path, 'w', encoding='utf-8')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for sitemap in SitemapFile.objects.order_by('id'):
            f.write("  <sitemap>\n")
            f.write(f"    <loc>{settings.APP_URL}/sitemaps/{sitemap.filename}</loc>\n")
            f.write(f"    <lastmod>{timezone.now().date()}</lastmod>\n")
            f.write("  </sitemap>\n")
        f.write("</sitemapindex>\n")
        f.close()
        print("Updated sitemap index")

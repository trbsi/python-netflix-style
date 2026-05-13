from src.core.utils.lang import get_language_codes
from src.media.services.manticore.manticore_base_service import ManticoreBaseService


class ManticoreSchemaService(ManticoreBaseService):
    def create_indexes(self):
        codes = get_language_codes()
        for code in codes:
            self.utils.sql(f"""
                CREATE TABLE IF NOT EXISTS {self._video_table(code)} (
                id BIGINT,
                title TEXT,
                thumbnail STRING,
                slug STRING,
                duration INT,
                categories TEXT,
                tags TEXT
            )""")
            self.utils.sql(f"""
                CREATE TABLE IF NOT EXISTS {self._video_tag_table(code)} (
                video_id BIGINT,
                tag STRING
            )""")

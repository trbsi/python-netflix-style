import os
import uuid

from django.core import signing
from openai import OpenAI

from automationapp import settings
from src.discovery.models import SearchQuery
from src.events.events import enqueue_search_event


class LlmPersonalizeSiteService():
    MODEL = 'llama-3.1-8b-instant'

    def personalize_site(self, text: str, session_id: str | None) -> str | None:
        enqueue_search_event(session_id, text)

        response = self.get_llm_reply(text)
        uuid_str = str(uuid.uuid4())

        SearchQuery.objects.create(
            uuid=uuid_str,
            raw_search_query=text,
            structured_search_query=response,
        )
        signed_value = signing.dumps({
            "query": text,
            "id": uuid_str,
        })

        return signed_value

    def get_llm_reply(self, tags: str) -> str:
        client = OpenAI(
            api_key=os.environ.get(settings.GROQ_API_KEY),
            base_url="https://api.groq.com/openai/v1",
        )

        prompt = """Parse adult search query into intent JSON. Group words by same person/action/setting. Groups: roles, kinks, setting, appearance, positions, acts, categories. Separate different participants. Scene-level in "scene". Output only: {"scene":{"kinks":[],"setting":[],"positions":[],"acts":[],"categories":[]},"participants":[{"roles":[],"appearance":[]},{"roles":[],"appearance":[]}]}

        Query: "{user_query}" """

        formatted_prompt = prompt.format(user_query=tags)

        response = client.responses.create(
            input=formatted_prompt,
            model=self.MODEL,
        )
        print(response.output_text)

        return response.output_text

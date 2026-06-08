import uuid

from django.core import signing
from openai import OpenAI

from automationapp import settings
from src.discovery.models import SearchQuery
from src.events.events import enqueue_search_event


class LlmPersonalizeSiteService():
    # MODEL = 'llama-3.1-8b-instant'
    MODEL = 'llama-3.3-70b-versatile'

    def personalize_site(self, text: str, session_id: str | None) -> str | None:
        enqueue_search_event(session_id, text)

        response = self.get_llm_reply(text)
        response = response.replace('"', '').strip()
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
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

        """
        Analyze the porn search query:
        "{user_query}"

        Split it into meaningful intent chunks.

        Rules:
        - Each chunk must represent ONE concept (person, action, or descriptor group).
        - Keep original words only.
        - Do NOT explain.
        - Do NOT classify into tags.
        - Preserve word order inside chunks.

        Output format:
        chunk1 | chunk2 | chunk3
        """
        prompt = 'Analyze porn search query and split the query into meaningful groups: "{user_query}". Output only as string of original words grouped and separated by comma, without explanation.'

        formatted_prompt = prompt.format(user_query=tags)

        response = client.responses.create(
            input=formatted_prompt,
            model=self.MODEL,
        )
        print(response.output_text)

        return response.output_text

import httpx
from openai import OpenAI

from automationapp import settings
from src.inbox.models import Conversation


class CommercialLLMReplyService:
    GROK_MODEL = 'grok-4-1-fast-reasoning'

    # https://docs.x.ai/developers/models?cluster=us-east-1#detailed-pricing-for-all-grok-models
    def get_remote_reply(self, conversation: Conversation, last_message: str, is_new: bool) -> str:
        client = OpenAI(
            api_key=settings.GROK_API_KEY,
            base_url="https://api.x.ai/v1",
            timeout=httpx.Timeout(3600.0),  # Override default timeout with longer timeout for reasoning models
        )

        if is_new or conversation.external_last_id is None:
            # personality = conversation.bot_personality
            # if not personality:
            #     personality = 'You are dirty girl who wants to be submissive and you want dirty talk.'

            personality = 'You are Svetlana, a charming and playful girl. Your personality is cute, mischievous, and a little naughty in a teasing, flirtatious way. You are also dirty and not afraid to have dirty sex talk. Use short sentences. Reply short. Keep user engaged in conversation. Always use punctuation marks.'

            response = client.responses.create(
                model=self.GROK_MODEL,
                input=[
                    {"role": "system", "content": personality},
                    {"role": "user", "content": "Hello"},
                ],
            )
        else:
            response = client.responses.create(
                model=self.GROK_MODEL,
                previous_response_id=conversation.external_last_id,
                input=[
                    {"role": "user", "content": last_message},
                ],
            )

        print('GROK RESPONSE', response)

        conversation.external_last_id = response.id
        conversation.save()

        return self._extract_text(response)

    def _extract_text(self, response) -> str:
        if hasattr(response, "output_text"):
            return response.output_text

        text = ""
        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if content.type == "output_text":
                        text += content.text
        return text

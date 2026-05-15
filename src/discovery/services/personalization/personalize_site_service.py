import re

import spacy
from django.core import signing
from spacy.cli import download

from src.discovery.models import TagAlias


class PersonalizeSiteService():
    def personalize_site(self, text: str) -> str | None:
        text = self.clean_query(text)
        text_array = self.to_tokens(text)
        tags = self.get_canonical_tags(text_array)

        if not tags:
            return None

        signed_value = signing.dumps({
            "tags": ','.join(tags),
        })

        return signed_value

    def clean_query(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def to_tokens(self, text: str) -> list:
        model_name = 'en_core_web_sm'
        try:
            nlp = spacy.load(model_name)
        except OSError:
            download(model_name)
            nlp = spacy.load(model_name)

        doc = nlp(text)
        # lemma is basically singular form of word
        tokens = [
            token.lemma_
            for token in doc
            if not token.is_stop
        ]

        return tokens

    def get_canonical_tags(self, tags: list) -> list | None:
        tags = (
            TagAlias.objects
            .filter(raw_tag__in=tags)
            .values_list('canonical_tag', flat=True)
        )
        if tags:
            tags = list(set(tags))
            return tags

        return None

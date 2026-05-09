from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer


class VectorCommand(BaseCommand):
    def handle(self, *args, **options):
        model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        text = """
        Title:
        Romantic amateur hotel encounter

        Categories:
        amateur, couples

        Tags:
        romantic, intimate, hotel, realistic

        Description:
        slow paced intimate couple encounter
        """
        embedding = model.encode(text)
        print(len(embedding))
       
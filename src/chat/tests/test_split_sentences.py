from django.test import TestCase

from src.chat.services.auto_reply.split_sentences_service import SplitSentencesService


class SplitSentencesTest(TestCase):
    def test_split_sentences(self):
        sentence = "How are you? I'm great. i love you. This is great! Fuck off man haha"
        service = SplitSentencesService()
        result = service.split_sentences(sentence)
        self.assertEqual(
            result,
            ['how are you?', "I'm great", 'I love you', 'this is great!', 'fuck off man haha']
        )
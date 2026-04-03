import random
import re


class SplitSentencesService():
    def split_sentences(self, sentence: str) -> list:
        sentences = re.split(r'(?<=[.!?])\s+', sentence)

        protected_word = {'i'}
        startswith = {"i'"}

        for index, sentence in enumerate(sentences):
            # Randomly strip punctuation at the end
            if sentence and sentence[-1] in {'.', '!'}:
                if random.choice([True, False]):
                    sentence = sentence[:-1]

            words = sentence.split()

            for i, word in enumerate(words):
                lower_word = word.lower()

                if lower_word in protected_word:
                    words[i] = word.capitalize()

                for start in startswith:
                    if lower_word.startswith(start):
                        words[i] = word.capitalize()

            sentence = " ".join(words)

            # Random capitalization
            if sentence and random.choice([True, False]):
                sentence = sentence[0].upper() + sentence[1:]

            sentences[index] = sentence

        return sentences

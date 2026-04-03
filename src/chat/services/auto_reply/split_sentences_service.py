import random
import re


class SplitSentencesService():

    def split_sentences(self, sentence: str) -> list:
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])', sentence)

        protected_word = {'i'}
        startswith = {"i'"}

        question_sentences = []
        normal_sentences = []

        for sentence in sentences:
            original_sentence = sentence  # keep original for later check

            # Randomly strip punctuation at the end (exclude '?')
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

            # Separate question sentences
            if original_sentence.strip().endswith('?'):
                question_sentences.append(sentence)
            else:
                normal_sentences.append(sentence)

        # Put questions at the end
        return normal_sentences + question_sentences

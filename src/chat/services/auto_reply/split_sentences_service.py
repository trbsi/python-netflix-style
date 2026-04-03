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
                sentence = sentence[0].lower() + sentence[1:]

            # Separate question sentences
            if original_sentence.strip().endswith('?'):
                question_sentences.append(sentence)
            else:
                normal_sentences.append(sentence)

        #  Put questions at the end
        sentences = normal_sentences + question_sentences

        # Randomly stitch sentences together
        stitched = []
        i = 0

        while i < len(sentences):
            current = sentences[i]

            # Decide randomly whether to merge with next sentence
            if i < len(sentences) - 1 and random.choice([True, False]):
                next_sentence = sentences[i + 1]

                # Join with space (or you can randomize this too)
                current = f"{current} {next_sentence}"
                i += 1  # skip next since it's merged

            stitched.append(current)
            i += 1

        return stitched

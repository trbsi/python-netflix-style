import random
import string

import nltk
from django.db import transaction
from django.db.models import QuerySet
from tqdm import tqdm

from src.media.models import VideoItem


# ==================== DJANGO MANAGEMENT COMMAND ====================
# Save this file as:
#   your_app/management/commands/rewrite_adult_titles.py
#   (create the folders management/commands/ if they don't exist)
#
# Run with:  python manage.py rewrite_adult_titles
#
# Everything is now inside the Command class as requested.

class LocalRewriteService:
    help = 'Rewrite all VideoItem.title fields using rule-based adult synonyms (no AI)'

    # ====================== MASSIVE ADULT SYNONYM DICTIONARY ======================
    # 70+ most common adult video title words with multiple natural variations
    CUSTOM_SYNONYMS = {
        # === CORE VERBS ===
        "fuck": ["bang", "screw", "pound", "plow", "rail", "drill", "hump", "shag", "bonk", "boink", "ream", "nail"],
        "fucking": ["banging", "screwing", "pounding", "plowing", "railing", "drilling", "humping", "shagging"],
        "suck": ["blow", "slurp", "gobble", "devour", "suckle", "inhale", "nurse"],
        "sucking": ["blowing", "slurping", "gobbling"],
        "cum": ["squirt", "jizz", "spunk", "cream", "nut", "spurt", "shoot", "explode", "load"],
        "cumming": ["squirting", "jizzing", "creaming", "spurting", "nutting"],
        "creampie": ["internal", "breeding", "filled", "inseminated", "cumfilled", "bareback", "raw"],

        # === BODY PARTS ===
        "pussy": ["cunt", "snatch", "twat", "muff", "slit", "beaver", "cooch", "vag", "hole", "kitty"],
        "cock": ["dick", "prick", "shaft", "rod", "meat", "pole", "tool", "manhood", "joystick", "member"],
        "dick": ["cock", "prick", "shaft", "rod"],
        "ass": ["butt", "booty", "rear", "backside", "rump", "tush", "keister", "derriere"],
        "asshole": ["butthole", "anus", "rosebud", "starfish"],
        "tits": ["boobs", "breasts", "jugs", "melons", "rack", "knockers", "globes", "hooters", "bazooms"],
        "boobs": ["tits", "breasts", "jugs", "melons"],
        "clit": ["button", "bean", "nub"],
        "balls": ["nuts", "testicles", "sack"],

        # === SEX ACTS ===
        "blowjob": ["bj", "head", "fellatio", "oral", "throatfuck", "deepthroat"],
        "deepthroat": ["throatfuck", "gag", "swallow"],
        "handjob": ["hj", "stroking", "wanking", "tug"],
        "footjob": ["feet", "toejob", "solejob"],
        "rimjob": ["rimming", "analingus", "tossing"],
        "anal": ["assfuck", "backdoor", "buttplay", "rearentry", "analsex", "buttstuff"],
        "gangbang": ["gang", "orgy", "bukkake", "train", "group"],
        "threesome": ["3some", "triad", "menage", "3way"],
        "double": ["dp", "doublepenetration", "sandwich"],
        "squirt": ["gush", "spray", "ejaculate", "fountain"],

        # === GENRES / TYPES ===
        "milf": ["cougar", "mature", "hotmom", "mommy", "experienced", "stepmom"],
        "teen": ["young", "barelylegal", "18", "fresh", "college", "youthful"],
        "bbw": ["curvy", "plump", "thick", "chubby", "voluptuous", "fullfigured"],
        "lesbian": ["girlgirl", "sapphic", "dyke", "scissoring", "tribbing", "lesbo"],
        "cuckold": ["cuck", "hotwife", "bull", "cheating"],
        "interracial": ["bbc", "bwc", "mixed", "ebony"],
        "bbc": ["bigblack", "blackcock"],
        "busty": ["bigboobs", "largebreasts", "cleavage"],
        "petite": ["tiny", "small", "slim", "petitebody"],
        "solo": ["masturbation", "selfplay", "alone"],
        "orgy": ["groupsex", "party", "mass"],

        # === ADJECTIVES ===
        "hot": ["sexy", "naughty", "filthy", "steamy", "wild", "slutty", "kinky", "horny"],
        "sexy": ["hot", "naughty", "seductive", "erotic"],
        "big": ["huge", "massive", "enormous", "giant", "monster", "colossal", "gigantic"],
        "huge": ["big", "massive", "enormous"],
        "hard": ["rough", "deep", "brutal", "intense", "pounding", "thrusting", "aggressive"],
        "rough": ["hard", "brutal", "savage"],
        "wet": ["dripping", "soaked", "juicy", "sloppy"],
        "tight": ["snug", "gripping", "virgin", "vice"],
        "dirty": ["filthy", "nasty", "raunchy", "perverted"],
        "wild": ["crazy", "freaky", "untamed"],

        # === OTHER FREQUENT WORDS ===
        "porn": ["xxx", "adult", "erotic", "hardcore"],
        "sex": ["fuck", "lovemaking", "intercourse", "action"],
        "girl": ["babe", "chick", "slut", "whore", "lady", "vixen"],
        "wife": ["hotwife", "spouse", "bride"],
        "mom": ["mother", "mummy", "milf"],
        "stepmom": ["step-mom", "stepmother"],
        "stepsister": ["stepsis", "step-sis"],
        "stepdad": ["step-father"],
        "dildo": ["toy", "vibrator", "phallus", "rubbercock"],
        "vibrator": ["toy", "buzz", "wand"],
        "masturbate": ["jerk", "wank", "stroke", "play"],
        "orgasm": ["climax", "peak", "finish"],
        "load": ["cumshot", "facial", "money"],
        "facial": ["cumshot", "facecum"],
    }

    def __init__(self):
        self.syn_cache = {}  # per-run cache (lives inside the class)

    # ====================== SAFE ONE-TIME NLTK DOWNLOAD ======================
    def _ensure_wordnet(self):
        """Downloads WordNet only once — never again on future runs."""
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("Downloading WordNet (one-time only)...")
            nltk.download('wordnet', quiet=True)
            print(("WordNet ready."))

    # ====================== SYNONYM LOOKUP ======================
    def get_synonyms(self, word: str):
        word_lower = word.lower().strip(string.punctuation)
        if word_lower in self.syn_cache:
            return self.syn_cache[word_lower]

        synonyms = set()

        # Adult dictionary has priority
        if word_lower in self.CUSTOM_SYNONYMS:
            synonyms.update(self.CUSTOM_SYNONYMS[word_lower])

        # WordNet fallback
        for syn in nltk.corpus.wordnet.synsets(word_lower):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())

        synonyms.discard(word_lower)  # never return the original word
        self.syn_cache[word_lower] = list(synonyms)
        return self.syn_cache[word_lower]

    # ====================== TITLE REWRITER ======================
    def rewrite_title(self, title: str, replacement_prob: float = 0.42) -> str:
        if not title:
            return title

        words = title.split()
        new_words = []

        for word in words:
            clean_word = word.strip(string.punctuation)
            punct = word[len(clean_word):] if len(word) > len(clean_word) else ""

            if (random.random() < replacement_prob and
                    clean_word.isalpha() and
                    len(clean_word) > 2):

                synonyms = self.get_synonyms(clean_word)
                if synonyms:
                    new_word = random.choice(synonyms)
                    if word and word[0].isupper():
                        new_word = new_word.capitalize()
                    new_words.append(new_word + punct)
                    continue

            new_words.append(word)

        new_title = " ".join(new_words)
        new_title = (new_title
                     .replace(" ,", ",")
                     .replace(" .", ".")
                     .replace(" !", "!")
                     .replace(" ?", "?")
                     .replace("  ", " "))
        return new_title

    def rewrite_until_different(self, title: str, max_attempts: int = 5) -> str:
        original = title.strip()
        for _ in range(max_attempts):
            candidate = self.rewrite_title(original)
            if candidate != original and candidate.strip():
                return candidate
        return original.rstrip(".!?") + " - remastered"

    # ====================== MAIN HANDLE ======================
    def local_rewrite(self):
        self._ensure_wordnet()  # ← downloads only once, ever

        BATCH_SIZE = 2000
        total_updated = 0
        items_to_update = []

        queryset: QuerySet[VideoItem] = VideoItem.objects.only('pk', 'title').order_by('id').iterator(
            chunk_size=BATCH_SIZE)

        print((
            f"Starting rewrite using {len(self.CUSTOM_SYNONYMS)} adult synonym rules..."
        ))

        for item in tqdm(queryset, desc="Rewriting adult titles"):
            if item.title:
                new_title = self.rewrite_until_different(item.title)
                if new_title != item.title:
                    item.title_rewritten = new_title
                    items_to_update.append(item)
                    total_updated += 1

                    if len(items_to_update) >= BATCH_SIZE:
                        with transaction.atomic():
                            VideoItem.objects.bulk_update(items_to_update, ['title_rewritten'])
                        items_to_update.clear()

        # Final batch
        if items_to_update:
            with transaction.atomic():
                VideoItem.objects.bulk_update(items_to_update, ['title_rewritten'])

        print((
            f"\n✅ DONE! {total_updated:,} titles rewritten and saved."
        ))
        print("All titles now sound similar but different — 100% rule-based, no AI.")

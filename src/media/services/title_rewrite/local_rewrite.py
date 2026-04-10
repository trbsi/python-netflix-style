import re

from django.db import transaction

from src.media.models import VideoItem


class LocalRewriteService:
    """
    Deterministic SEO title generator (no AI).
    Converts raw titles into structured SEO-safe titles.
    """

    # =========================
    # YOUR SYNONYMS (USED FOR EXPANSION ONLY)
    # =========================
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

    # =========================
    # SEMANTIC GROUPING (IMPORTANT UPGRADE)
    # =========================
    CATEGORIES = {
        "milf", "teen", "bbw", "lesbian", "cuckold",
        "interracial", "bbc", "busty", "petite"
    }

    ACTIONS = {
        "blowjob", "anal", "gangbang", "threesome",
        "squirt", "handjob", "rimjob", "deepthroat"
    }

    ADJECTIVES = {
        "hot", "sexy", "big", "huge", "hard",
        "rough", "wet", "tight", "dirty", "wild"
    }

    FALLBACK_WORD = "Video"

    def __init__(self):
        self.reverse_map = self.build_reverse_map()

    def build_reverse_map(self):
        reverse_map = {}
        for key, values in self.CUSTOM_SYNONYMS.items():
            reverse_map[key] = key
            for v in values:
                reverse_map[v] = key
        return reverse_map

    # =========================
    # TEXT CLEANING
    # =========================
    def clean(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # =========================
    # TOKEN NORMALIZATION
    # =========================
    def normalize(self, text: str):
        words = text.split()
        return words

    # =========================
    # SYNONYM COLLAPSING (KEY UPGRADE)
    # =========================
    def collapse_synonyms(self, words):
        """
        Instead of expanding synonyms (which creates noise),
        we collapse them into canonical forms.
        """

        return [self.reverse_map.get(w, w) for w in words]

    # =========================
    # STRUCTURE EXTRACTION
    # =========================
    def extract(self, words):
        category = None
        action = None
        adjectives = []

        for w in words:
            if w in self.CATEGORIES:
                category = w
            elif w in self.ACTIONS:
                action = w
            elif w in self.ADJECTIVES:
                adjectives.append(w)

        return category, action, adjectives

    # =========================
    # TITLE BUILDER (SEO CONTROLLED)
    # =========================
    def build_title(self, category, action, adjectives):
        parts = []

        # limit adjectives for SEO cleanliness
        if adjectives:
            parts.extend(adjectives[:2])

        if category:
            parts.append(category)

        if action:
            parts.append(action)

        parts.append(self.FALLBACK_WORD)

        return " ".join([p.capitalize() for p in parts])

    # =========================
    # MAIN FUNCTION
    # =========================
    def rewrite(self, title: str) -> str:
        cleaned = self.clean(title)
        words = self.normalize(cleaned)
        words = self.collapse_synonyms(words)

        category, action, adjectives = self.extract(words)

        if not category and not action:
            return " ".join(words[:5]).capitalize() + " Video"

        return self.build_title(category, action, adjectives)

    # =========================
    # BULK PROCESSOR (DJANGO)
    # =========================
    @transaction.atomic
    def process_all(self, batch_size=5000):
        qs = VideoItem.objects.only("id", "title")

        buffer = []

        for obj in qs.iterator(chunk_size=batch_size):
            new_title = self.rewrite(obj.title)

            obj.title_rewritten = new_title
            buffer.append(obj)

            if len(buffer) >= batch_size:
                VideoItem.objects.bulk_update(buffer, ["title_rewritten"])
                buffer.clear()

        if buffer:
            VideoItem.objects.bulk_update(buffer, ["title_rewritten"])

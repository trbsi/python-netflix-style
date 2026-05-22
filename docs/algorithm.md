# Formula

## 1. Average Group Weight

**What it represents:**
How important the matched concepts are in your taxonomy.

**In plain terms:**
roles > acts > categories
some types of meaning matter more than others

**Purpose:**

- it injects semantic hierarchy into ranking.

**Effect:**

- boosts meaningful categories (e.g. roles, dynamics)
- reduces importance of weak signals (e.g. generic tags)

## 2. Coverage

**What it represents:**
How much of the user’s query is satisfied.

**In plain terms:**
did we match everything the user asked for?

**Purpose:**

- It ensures completeness of match.

**Effect:**

- full matches rank higher
- partial matches are penalized

## 3. Match Quality

**What it represents:**
How well the video matches the important parts of the query.

**In plain terms:**
not all query terms are equal
matching “milf” is more important than matching “outdoor” in many cases

**Purpose:**

- It enforces semantic alignment between query intent and video content.

**Effect:**

- videos matching important query concepts rank higher
- irrelevant or weak matches are downgraded

## 4. Rarity Score

**What it represents:**
How rare or specific the matched tags are in your dataset.

**In plain terms:**
common tags = low value.
rare tags = high value

**Purpose:**

- It adds information value weighting.

**Effect:**

- boosts specific/niche matches
- reduces dominance of generic tags

--- 

# Video Ranking Algorithm (Based on Your Code)

This function takes a list of **canonical tag slugs**, expands them into raw tags, retrieves candidate videos, and ranks
them using a weighted semantic scoring system.

---

# High-Level Idea

You are NOT doing simple tag matching.

You are computing:

> how well a video matches the *semantic structure* of a user query

using:

- group importance
- coverage of query
- semantic match strength
- rarity of tags

---

# Step 1 — Canonical Tags → Raw Tags

Input:

```python
canonical_tag_slugs = ["goth", "milf", "outdoor", "blowjob"]
``` 

Each canonical tag is resolved into:

- raw tags (aliases)
- group weight (roles, acts, etc.)
- rarity score

Example:

| Canonical | Raw Tags                   |
|-----------|----------------------------|
| milf      | milf, cougar, mature-woman |
| goth      | goth, alternative          |
| blowjob   | blowjob                    |

# Step 2 — Build Tag Metadata

Each raw tag becomes:

```
TagAliasMeta(
    group_weight,
    rarity_score
)
```

| Tag     | Group      | Group Weight | Rarity |
|---------|------------|--------------|--------|
| milf    | roles      | 4.5          | 1.8    |
| goth    | appearance | 3.0          | 4.2    |
| blowjob | acts       | 2.0          | 0.5    |

# Step 3 — Query-Level Statistics

Total query tags:
**N = number of raw tags**

Total query weight:
**total_raw_tags_weight = sum(group_weight of all raw tags)**

Average group weight:
**group_weight = total_raw_tags/total_raw_tags_weight**.
This represents average importance per query tag

# Step 4 — Retrieve Candidate Videos

You search Manticore. Result:

- Video A
    - milf, goth, outdoor, blowjob
- Video B
    - milf, blowjob

# Step 5 — Compute Ranking Signals

### 1. Coverage

How much of the query is matched:
**coverage = matched_tag_count/raw_tags_count**

Example:

- Video A → 4/4 = 1.0
- Video B → 2/4 = 0.5

### 2. Match Quality

How important matched tags are:
**match_quality = sum(matched_group_weights)/total_raw_tags_weight**

Example:

- Video A → matches roles + appearance + acts → high
- Video B → mostly acts → lower

### 3. Rarity Score

How informative matched tags are:
**rarity_score = average(tag rarity)**

Example:

- “blowjob” → low rarity
- “goth milf” → high rarity

# Step 6 — Final Video Score

Your final formula:

score=group_weight×coverage×match_quality×rarity_score
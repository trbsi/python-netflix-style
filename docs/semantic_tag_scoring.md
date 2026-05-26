# Semantic tag scoring

Related-tag expansion is a secondary boost layered on top of the existing direct
tag score.

Example:

```python
query_tags = ["bear", "daddy"]

expanded_related_tags = {
    "bear": [
        {"related_tag_slug": "hairy", "score": 0.9},
    ],
    "daddy": [
        {"related_tag_slug": "mature", "score": 0.6},
    ],
}

candidate_video_tags = ["hairy", "mature"]

direct_score = 0.0
related_score = 0.9 + 0.6
final_score = direct_score + related_score
```

Computed scores:

```python
{
    "direct_score": 0.0,
    "related_score": 1.5,
    "final_score": 1.5,
}
```

If a video contains `bear` directly, that canonical tag is scored only by the
direct scoring formula and is excluded from related scoring.

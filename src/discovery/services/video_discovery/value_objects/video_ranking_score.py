from dataclasses import dataclass, field


@dataclass
class VideoRankingScore:
    video_id: int
    final_score: float

    direct_score: float
    direct_matched_tags: list[str] = field(default_factory=list)

    related_matched_tags: list[str] = field(default_factory=list)
    related_score: float = 0,

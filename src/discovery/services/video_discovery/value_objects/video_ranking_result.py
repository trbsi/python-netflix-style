from dataclasses import dataclass

from src.discovery.services.video_discovery.value_objects.video_ranking_score import VideoRankingScore


@dataclass
class VideoRankingResult:
    items: list[VideoRankingScore]
    expanded_related_tags: dict[str, list]

    def get_video_ids(self) -> list[int]:
        return [item.video_id for item in self.items]

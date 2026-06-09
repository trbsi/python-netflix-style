from dataclasses import dataclass


@dataclass
class VideoStructuredMatch:
    video_id: int
    role_matched: int = 0
    appearance_matched: int = 0
    trait_matched: int = 0
    interaction_matched: int = 0
    setting_matched: int = 0

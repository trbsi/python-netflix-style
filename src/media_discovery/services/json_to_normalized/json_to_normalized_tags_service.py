import traceback

from src.media.models import VideoItem
from src.media_discovery.models import Interaction, Participant
from src.media_discovery.models import Tag


class JsonToNormalizedTagsService(object):
    def insert_normalized_tags(self):
        videos = VideoItem.objects.only("id", "video_metadata").iterator(chunk_size=1000)

        for video in videos:
            try:
                metadata = video.video_metadata or {}
                participants = metadata.get('participants', [])
                acts = metadata.get('acts', [])
                participant_map = {}

                Participant.objects.filter(video=video).delete()

                for participant_data in participants:
                    participant = Participant.objects.create(video=video)
                    participant_map[str(participant_data.get("id"))] = participant
                    participant_tag_ids = self._participant_tags(participant_data)

                    if participant_tag_ids:
                        participant.tags.set(participant_tag_ids)

                for act_data in acts:
                    from_participant = participant_map.get(str(act_data.get("from")))
                    to_participant = participant_map.get(str(act_data.get("to")))
                    act = Tag.objects.filter(name=act_data.get("act")).first()

                    if not act:
                        print(f"Missing act for video: {video.id} {act_data}")
                        continue

                    interaction = Interaction.objects.create(
                        video=video,
                        from_participant=from_participant,
                        to_participant=to_participant,
                        act=act,
                    )

                    kinks = [
                        kink_name
                        for kink_name in act_data.get("kink", [])
                    ]

                    if kinks:
                        kink_ids = Tag.objects.filter(name__in=kinks).values_list("id", flat=True)
                        interaction.kinks.set(kink_ids)
            except Exception as e:
                print(video.id)
                print(e, traceback.format_exc())

    def _participant_tags(self, participant_data: dict) -> list:
        participant_tags = []

        for group in ("role", "appearance"):
            for tag_name in participant_data.get(group):
                participant_tags.append(tag_name)

        tags = Tag.objects.filter(name__in=participant_tags).values_list("id", flat=True)
        return list(tags)

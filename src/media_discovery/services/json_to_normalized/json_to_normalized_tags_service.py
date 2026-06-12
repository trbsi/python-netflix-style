from src.media.models import VideoItem
from src.media_discovery.models import Interaction, Participant


class JsonToNormalizedTagsService(object):
    def insert_normalized_tags(self):
        videos = VideoItem.objects.only("id", "video_metadata").iterator(chunk_size=1000)

        for video in videos:
            metadata = video.video_metadata or {}
            participants = metadata.get('participants', [])
            acts = metadata.get('acts', [])
            participant_map = {}

            Participant.objects.filter(video=video).delete()

            for participant_data in participants:
                participant = Participant.objects.create(video=video)
                participant_map[str(participant_data.get("id"))] = participant
                participant_tags = self._participant_tags(participant_data)

                if participant_tags:
                    participant.tags.set(participant_tags)

            for act_data in acts:
                from_participant = participant_map.get(str(act_data.get("from")))
                to_participant = participant_map.get(str(act_data.get("to")))
                act = act_data.get("act")

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
                    interaction.kinks.set(kinks)

    def _participant_tags(self, participant_data):
        participant_tags = []

        for group in ("role", "appearance"):
            for tag_name in participant_data.get(group):
                participant_tags.append(tag_name)

        return participant_tags

from django.db.models import QuerySet, Max
from django.utils.text import slugify
from xai_sdk import Client
from xai_sdk.chat import system, user

from automationapp import settings
from src.media.models import VideoItem, TranslationBatch


class AiRewriteService:
    GROK_MODEL = 'grok-4-1-fast-reasoning'

    # https://docs.x.ai/developers/models?cluster=us-east-1#detailed-pricing-for-all-grok-models
    # https://docs.x.ai/developers/advanced-api-usage/batch-api
    def send_to_batch(self, batch_size: int):
        client = Client(api_key=settings.GROK_API_KEY)

        batch: TranslationBatch = TranslationBatch.objects.order_by('-id').first()
        if batch:
            last_id = batch.last_id
        else:
            last_id = VideoItem.objects.aggregate(Max('id'))['id__max']

        videos: QuerySet[VideoItem] = (
            VideoItem.objects
            .filter(title_rewritten__isnull=True)
            .filter(id__lt=last_id)
            .order_by('-id')[:batch_size]
        )

        if not videos:
            return

        feedback_data = []
        for video in videos:
            feedback_data.append({"id": str(video.id), "text": video.title})

        # Step 1: Create a batch
        print("Creating batch...")
        batch = client.batch.create(batch_name="title_rewrite")
        print(f"Batch created: {batch.batch_id}")

        # Step 2: Build and add requests
        print("Adding requests...")
        batch_requests = []
        for item in feedback_data:
            chat = client.chat.create(
                model=self.GROK_MODEL,
                batch_request_id=item["id"],
            )
            chat.append(system(
                "Rewrite title. Make it SEO friendly. Respond with only new title."
            ))
            chat.append(user(item["text"]))
            batch_requests.append(chat)

        client.batch.add(batch_id=batch.batch_id, batch_requests=batch_requests)
        print(f"Added {len(batch_requests)} requests")

        model = TranslationBatch()
        model.batch_id = batch.batch_id
        model.status = 'started'
        model.last_id = feedback_data[-1]['id']
        model.save()

    def check_and_save_batch_result(self):
        client = Client(api_key=settings.GROK_API_KEY)
        batches = TranslationBatch.objects.filter(status='started')

        for batch in batches:
            # Step 3: Wait for completion
            print("\nProcessing...")
            remote_batch = client.batch.get(batch_id=batch.batch_id)
            pending = remote_batch.state.num_pending
            completed = remote_batch.state.num_success + remote_batch.state.num_error

            print(f"{completed}/{remote_batch.state.num_requests} complete")

            if pending > 0:
                continue

            # Step 4: Retrieve and display results
            print("--- Results ---")
            results = client.batch.list_batch_results(batch_id=remote_batch.batch_id)

            field = VideoItem._meta.get_field('slug_rewritten')
            for result in results.succeeded:
                try:
                    video: VideoItem = VideoItem.objects.get(id=result.batch_request_id)
                    new_title = result.response.content.strip()
                    video.title_rewritten = new_title
                    video.slug_rewritten = slugify(new_title)[:field.max_length]
                    video.save()
                except Exception as e:
                    print(e)

            # Report any failures
            if results.failed:
                print("--- Errors ---")
                for result in results.failed:
                    print(f"[{result.batch_request_id}] {result.error_message}")

            # Display cost
            cost_usd = batch.cost_breakdown.total_cost_usd_ticks / 1e10
            print("\nTotal cost: $%.4f" % cost_usd)

            batch.status = 'finished'
            batch.save()

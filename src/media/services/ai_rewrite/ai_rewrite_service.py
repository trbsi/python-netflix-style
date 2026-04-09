import time

from django.db.models import QuerySet
from django.template.defaultfilters import slugify
from xai_sdk import Client
from xai_sdk.chat import system, user

from automationapp import settings
from src.media.models import VideoItem


class AiRewriteService:
    GROK_MODEL = 'grok-4-1-fast-reasoning'

    # https://docs.x.ai/developers/models?cluster=us-east-1#detailed-pricing-for-all-grok-models
    # https://docs.x.ai/developers/advanced-api-usage/batch-api
    def rewrite_title(self, batch_size: int):
        client = Client(api_key=settings.GROK_API_KEY)

        videos: QuerySet[VideoItem] = (VideoItem.objects
        .filter(title_rewritten__isnull=True).order_by('-id')[:batch_size])

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

        # Step 3: Wait for completion
        print("\nProcessing...")
        while True:
            batch = client.batch.get(batch_id=batch.batch_id)
            pending = batch.state.num_pending
            completed = batch.state.num_success + batch.state.num_error

            print(f"{completed}/{batch.state.num_requests} complete")

            if pending == 0:
                break
            time.sleep(2)

        # Step 4: Retrieve and display results
        print("\n--- Results ---")
        results = client.batch.list_batch_results(batch_id=batch.batch_id)

        for result in results.succeeded:
            try:
                video: VideoItem = VideoItem.objects.get(id=result.batch_request_id)
                new_title = result.response.content.strip()
                video.title_rewritten = new_title
                video.slug_rewritten = slugify(new_title)
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

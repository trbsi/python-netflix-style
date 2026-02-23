class UpdateMediaService():
    def update_media(self):
        post = get_object_or_404(PostContent, id=post_id, user=request.user)
        if request.POST.get("delete_file"):
            if post.file_name:
                path = post.get_file_path()
                if os.path.exists(path):
                    os.remove(path)
            post.delete()
        else:
            post.content_type = request.POST.get("content_type")
            post.site = request.POST.get("site")
            post.site_username = request.POST.get("site_username")
            post.title = request.POST.get("title")
            post.content = request.POST.get("content")
            post.timezone = request.POST.get("timezone")
            post.status = request.POST.get("status")

            file = request.FILES.get("file")
            if file:
                fs = FileSystemStorage()
                post.file_name = fs.save(file.name, file)

            post.save()

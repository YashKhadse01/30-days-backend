
from django.contrib import admin
from django.utils import timezone

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "created_at",
        "published_at",
    )

    list_filter = (
        "status",
        "created_at",
        "author",
    )

    search_fields = (
        "title",
        "content",
        "author__username",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 20

    actions = [
        "publish_posts",
        "unpublish_posts",
    ]

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        updated = queryset.update(
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.message_user(
            request,
            f"{updated} posts published successfully.",
        )

    @admin.action(description="Move selected posts to draft")
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(
            status=Post.Status.DRAFT,
            published_at=None,
        )
        self.message_user(
            request,
            f"{updated} posts moved to draft.",
        )

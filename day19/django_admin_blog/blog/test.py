
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post

User = get_user_model()


class BlogTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(
            username="blog_author",
            password="SecurePassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_user",
            password="SecurePassword123!",
        )

        self.post = Post.objects.create(
            title="First Django Post",
            slug="first-django-post",
            content="Learning Django testing.",
            author=self.author,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_post_creation(self):
        """A blog post can be saved to the database."""
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(self.post.author, self.author)
        self.assertEqual(
            self.post.status,
            Post.Status.PUBLISHED,
        )

    def test_post_string_representation(self):
        """The string representation returns the title."""
        self.assertEqual(
            str(self.post),
            "First Django Post",
        )

    def test_automatic_slug_generation(self):
        """A slug is generated when not supplied."""
        post = Post.objects.create(
            title="My Automatic Slug",
            content="Slug generation test.",
            author=self.author,
        )

        self.assertEqual(
            post.slug,
            "my-automatic-slug",
        )

    def test_absolute_url(self):
        """A post generates its correct detail URL."""
        self.assertEqual(
            self.post.get_absolute_url(),
            reverse(
                "blog:post_detail",
                kwargs={"slug": self.post.slug},
            ),
        )

    def test_published_post_visible(self):
        """Published posts appear on the blog listing."""
        response = self.client.get(
            reverse("blog:post_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "First Django Post",
        )

    def test_draft_post_hidden(self):
        """Draft posts do not appear on the public listing."""
        Post.objects.create(
            title="Secret Draft Post",
            slug="secret-draft-post",
            content="Not published yet.",
            author=self.author,
            status=Post.Status.DRAFT,
        )

        response = self.client.get(
            reverse("blog:post_list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Secret Draft Post",
        )

    def test_post_detail(self):
        """Published post details are accessible."""
        response = self.client.get(
            self.post.get_absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Learning Django testing.",
        )

    def test_anonymous_user_cannot_create(self):
        """Anonymous users must log in before creating."""
        response = self.client.get(
            reverse("blog:post_create")
        )

        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_create(self):
        """Authenticated users can create posts."""
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("blog:post_create"),
            {
                "title": "Created Through Form",
                "slug": "created-through-form",
                "content": "Testing CreateView.",
                "status": Post.Status.PUBLISHED,
            },
        )

        self.assertEqual(response.status_code, 302)

        created = Post.objects.get(
            slug="created-through-form"
        )

        self.assertEqual(created.author, self.author)
        self.assertIsNotNone(created.published_at)

    def test_author_can_update_post(self):
        """The post author can edit their own post."""
        self.client.force_login(self.author)

        response = self.client.post(
            reverse(
                "blog:post_update",
                kwargs={"slug": self.post.slug},
            ),
            {
                "title": "Updated Django Post",
                "slug": self.post.slug,
                "content": "Updated content.",
                "status": Post.Status.PUBLISHED,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.title,
            "Updated Django Post",
        )

    def test_other_user_cannot_update_post(self):
        """Users cannot edit another author's post."""
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                "blog:post_update",
                kwargs={"slug": self.post.slug},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_author_can_delete_post(self):
        """The post author can delete their post."""
        self.client.force_login(self.author)

        response = self.client.post(
            reverse(
                "blog:post_delete",
                kwargs={"slug": self.post.slug},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Post.objects.filter(
                pk=self.post.pk
            ).exists()
        )

    def test_other_user_cannot_delete_post(self):
        """Users cannot delete another author's post."""
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                "blog:post_delete",
                kwargs={"slug": self.post.slug},
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Post.objects.filter(
                pk=self.post.pk
            ).exists()
        )

    def test_admin_bulk_publish(self):
        """Admin can publish selected draft posts."""
        self.author.is_staff = True
        self.author.is_superuser = True
        self.author.save()

        draft = Post.objects.create(
            title="Admin Publish Test",
            slug="admin-publish-test",
            content="Draft content.",
            author=self.author,
            status=Post.Status.DRAFT,
        )

        self.client.force_login(self.author)

        response = self.client.post(
            reverse("admin:blog_post_changelist"),
            {
                "action": "publish_posts",
                "_selected_action": [draft.pk],
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 302)

        draft.refresh_from_db()

        self.assertEqual(
            draft.status,
            Post.Status.PUBLISHED,
        )
        self.assertIsNotNone(draft.published_at)

    def test_admin_bulk_unpublish(self):
        """Admin can move published posts to draft."""
        self.author.is_staff = True
        self.author.is_superuser = True
        self.author.save()

        self.client.force_login(self.author)

        response = self.client.post(
            reverse("admin:blog_post_changelist"),
            {
                "action": "unpublish_posts",
                "_selected_action": [self.post.pk],
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.status,
            Post.Status.DRAFT,
        )
        self.assertIsNone(self.post.published_at)


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import PostForm
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        return (
            Post.objects.filter(
                status=Post.Status.PUBLISHED
            )
            .select_related("author")
            .order_by("-published_at", "-created_at")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Post.objects.filter(
            status=Post.Status.PUBLISHED
        ).select_related("author")

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user

        if form.instance.status == Post.Status.PUBLISHED:
            form.instance.published_at = timezone.now()

        return super().form_valid(form)


class PostUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")

    def test_func(self):
        return self.get_object().author_id == self.request.user.pk

    def form_valid(self, form):
        if form.instance.status == Post.Status.PUBLISHED:
            if form.instance.published_at is None:
                form.instance.published_at = timezone.now()
        else:
            form.instance.published_at = None

        return super().form_valid(form)


class PostDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def test_func(self):
        return self.get_object().author_id == self.request.user.pk


from django.urls import path

from .views import (
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListView,
    PostUpdateView,
)

app_name = "blog"

urlpatterns = [
    path(
        "",
        PostListView.as_view(),
        name="post_list",
    ),
    path(
        "posts/create/",
        PostCreateView.as_view(),
        name="post_create",
    ),
    path(
        "posts/<slug:slug>/",
        PostDetailView.as_view(),
        name="post_detail",
    ),
    path(
        "posts/<slug:slug>/edit/",
        PostUpdateView.as_view(),
        name="post_update",
    ),
    path(
        "posts/<slug:slug>/delete/",
        PostDeleteView.as_view(),
        name="post_delete",
    ),
]

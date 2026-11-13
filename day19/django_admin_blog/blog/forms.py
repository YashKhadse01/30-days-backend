
from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "content",
            "status",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter post title",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter unique slug",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Write your blog post...",
                }
            ),
            "status": forms.Select(
                attrs={"class": "form-control"}
            ),
        }

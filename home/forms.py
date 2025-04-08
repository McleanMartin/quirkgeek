from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 1,
            'placeholder': 'Add a comment...',
            'class': 'comment-input'
        }),
        label=''
    )
    
    class Meta:
        model = Comment
        fields = ['text']
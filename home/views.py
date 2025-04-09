from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import BlogPage, Comment

@require_POST
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(BlogPage, id=post_id)
    user = request.user
    
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    
    # Return the updated like button HTML
    context = {
        'page': post,
        'request': request
    }
    return render(request, 'home/includes/like_button.html', context)

@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(BlogPage, id=post_id)
    text = request.POST.get('text', '').strip()
    
    if not text:
        return render(request, 'home/includes/comment_error.html', {
            'error': 'Comment text is required'
        }, status=400)
    
    comment = Comment.objects.create(
        blog_page=post,
        user=request.user,
        text=text
    )
    
    # Return the new comment HTML
    return render(request, 'home/includes/comment.html', {
        'comment': comment,
        'request': request
    })

@require_POST
@login_required
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    
    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)
    
    # Return the updated comment HTML
    return render(request, 'home/includes/comment.html', {
        'comment': comment,
        'request': request
    })
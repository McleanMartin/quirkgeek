from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import BlogPage, Comment
import json

@require_POST
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(BlogPage, id=post_id)
    user = request.user
    
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes()
    })

@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(BlogPage, id=post_id)
    
    # Check if request is AJAX/HTMX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            text = data.get('text')
        except json.JSONDecodeError:
            # Fallback to form data if JSON parsing fails
            text = request.POST.get('text')
    else:
        # Standard form submission
        text = request.POST.get('text')
    
    if not text:
        return JsonResponse({'success': False, 'error': 'Comment text is required'}, status=400)
    
    comment = Comment.objects.create(
        blog_page=post,
        user=request.user,
        text=text
    )
    
    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'text': comment.text,
            'username': comment.user.username,
            'created_at': comment.created_at.strftime("%b %d, %Y"),
            'total_likes': 0,
            'user_avatar': comment.user.profile.avatar.url if hasattr(comment.user, 'profile') and comment.user.profile.avatar else '/static/images/default-avatar.jpg'
        }
    })

@require_POST
@login_required
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    
    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'total_likes': comment.total_likes()
    })
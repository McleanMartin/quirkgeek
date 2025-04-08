document.addEventListener('DOMContentLoaded', function() {
    // Like post functionality
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            toggleLike(postId, this);
        });
    });
    
    // Like comment functionality
    document.querySelectorAll('.like-comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.closest('.comment').getAttribute('data-comment-id');
            toggleCommentLike(commentId, this);
        });
    });
    
    // Add comment functionality
    document.querySelectorAll('.add-comment-form').forEach(form => {
        const input = form.querySelector('.comment-input');
        const submitBtn = form.querySelector('.post-comment-btn');
        
        input.addEventListener('input', function() {
            submitBtn.disabled = this.value.trim() === '';
        });
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const postId = this.getAttribute('data-post-id');
            const text = input.value.trim();
            
            if (text) {
                addComment(postId, text, this);
                input.value = '';
                submitBtn.disabled = true;
            }
        });
    });
});

function toggleLike(postId, element) {
    fetch(`/toggle-like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            element.innerHTML = '<i class="fas fa-heart"></i>';
            element.querySelector('i').style.color = '#ed4956';
        } else {
            element.innerHTML = '<i class="far fa-heart"></i>';
        }
        element.nextElementSibling.textContent = data.total_likes;
    });
}

function toggleCommentLike(commentId, element) {
    fetch(`/toggle-comment-like/${commentId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        const icon = element.querySelector('i');
        const countElement = element.querySelector('.comment-like-count');
        
        if (data.liked) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            icon.style.color = '#ed4956';
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            icon.style.color = '';
        }
        countElement.textContent = data.total_likes;
    });
}

function addComment(postId, text, formElement) {
    fetch(`/add-comment/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commentsList = formElement.previousElementSibling;
            const newComment = document.createElement('div');
            newComment.className = 'comment';
            newComment.setAttribute('data-comment-id', data.comment.id);
            newComment.innerHTML = `
                <div class="comment-header">
                    <img src="${data.comment.user_avatar}" alt="${data.comment.username}" class="comment-avatar">
                    <span class="comment-username">${data.comment.username}</span>
                    <span class="comment-time">Just now</span>
                </div>
                <div class="comment-text">${data.comment.text}</div>
                <div class="comment-actions">
                    <button class="like-comment-btn">
                        <i class="far fa-heart"></i>
                        <span class="comment-like-count">${data.comment.total_likes}</span>
                    </button>
                </div>
            `;
            commentsList.prepend(newComment);
            
            // Add event listener to new like button
            newComment.querySelector('.like-comment-btn').addEventListener('click', function() {
                toggleCommentLike(data.comment.id, this);
            });
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
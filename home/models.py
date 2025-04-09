from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel,TabbedInterface, ObjectList
from wagtail import blocks
from wagtail.images.models import Image
from django.core.paginator import Paginator
from wagtail.snippets.models import register_snippet
from wagtail.search import index

User = get_user_model()

# ============== CORE MODELS ==============

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class HomePage(Page):
    author_name = models.CharField(max_length=100, default="Developer")
    intro = RichTextField(features=['bold', 'italic', 'link'], blank=True)
    profile_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('code', blocks.TextBlock()),
        ('terminal_command', blocks.CharBlock()),
    ], use_json_field=True, blank=True, null=True)
    
    
    content_panels = Page.content_panels + [
        FieldPanel('author_name'),
        FieldPanel('intro'),
        FieldPanel('profile_image'),
        FieldPanel('body'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get all live blog posts ordered by date
        all_posts = BlogPage.objects.live().order_by('-date')
        
        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(all_posts, 6)
        
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['recent_posts'] = posts
        context['featured_projects'] = ProjectPage.objects.live().filter(featured=True)[:3]
        context['technologies'] = Technology.objects.all()[:8]
        return context

# ============== BLOG MODELS ==============

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(features=['h2', 'h3', 'bold', 'italic', 'link', 'code', 'blockquote'])
    # technologies = models.ManyToManyField('Technology', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        blank=True
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('cover_image'),
        FieldPanel('body'),
        # FieldPanel('technologies'),
        FieldPanel('tags'),
        InlinePanel('post_comments', label="Comments"),
    ]

    def total_likes(self):
        return self.likes.count()
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['comments'] = self.post_comments.filter(parent__isnull=True).order_by('-created_at')
        return context

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        blog_posts = BlogPage.objects.live().order_by('-date')
        context['blog_posts'] = blog_posts
        return context

# ============== PROJECT MODELS ==============

class ProjectPage(Page):
    date = models.DateField("Project date")
    summary = models.CharField(max_length=250)
    body = RichTextField(features=['h2', 'h3', 'bold', 'italic', 'link', 'code'])
    technologies = models.ManyToManyField('Technology', blank=True)
    featured = models.BooleanField(default=False)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    screenshot = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('summary'),
        FieldPanel('body'),
        FieldPanel('technologies'),
        FieldPanel('featured'),
        FieldPanel('screenshot'),
        FieldPanel('github_url'),
        FieldPanel('live_url'),
    ]

class ProjectIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['projects'] = ProjectPage.objects.live().order_by('-date')
        return context

# ============== SOCIAL FEATURES ==============

class Comment(models.Model):
    blog_page = ParentalKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name='post_comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User,
        related_name='liked_comments',
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog_page.title}"
    
    def total_likes(self):
        return self.likes.count()
    
    def total_replies(self):
        return self.replies.count()

# ============== SNIPPETS ==============

@register_snippet
class Technology(index.Indexed, models.Model):
    name = models.CharField(max_length=255, unique=True)
    icon_class = models.CharField(
        max_length=255,
        blank=True,
        help_text="Font Awesome class (e.g., 'fab fa-python')"
    )
    description = RichTextField(blank=True, null=True)
    documentation_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Search configuration
    search_fields = [
        index.SearchField('name', partial_match=True),
        index.FilterField('is_active'),
    ]
    
    # Panels configuration
    general_panels = [
        FieldPanel('name'),
        FieldPanel('icon_class'),
        FieldPanel('is_active'),
    ]
    
    info_panels = [
        FieldPanel('description'),
        FieldPanel('documentation_url'),
    ]
    
    edit_handler = TabbedInterface([
        ObjectList(general_panels, heading='General'),
        ObjectList(info_panels, heading='Info'),
    ])
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ['name']

# ============== USER PROFILES ==============

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.jpg'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
from wagtail import hooks
from wagtail.admin.forms import WagtailAdminPageForm
from django import forms
from .models import BlogPage, ProjectPage

class BlogPageForm(WagtailAdminPageForm):
    def save(self, commit=True):
        # Get the unsaved instance
        instance = super().save(commit=False)
        
        # Store M2M data temporarily
        if 'technologies' in self.cleaned_data:
            technologies = self.cleaned_data['technologies']
            instance._pending_technologies = technologies
            del self.cleaned_data['technologies']
        
        if 'tags' in self.cleaned_data:
            tags = self.cleaned_data['tags']
            instance._pending_tags = tags
            del self.cleaned_data['tags']
        
        # First save to create the page
        if commit:
            instance.save()
            self.save_m2m()
            
            # Now add the M2M relationships
            if hasattr(instance, '_pending_technologies'):
                instance.technologies.set(instance._pending_technologies)
            if hasattr(instance, '_pending_tags'):
                instance.tags.set(instance._pending_tags)
        
        return instance

class ProjectPageForm(WagtailAdminPageForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'technologies' in self.cleaned_data:
            technologies = self.cleaned_data['technologies']
            instance._pending_technologies = technologies
            del self.cleaned_data['technologies']
        
        if commit:
            instance.save()
            self.save_m2m()
            
            if hasattr(instance, '_pending_technologies'):
                instance.technologies.set(instance._pending_technologies)
        
        return instance

@hooks.register('register_page_form_class')
def register_page_forms(cls):
    if cls == BlogPage:
        return BlogPageForm
    elif cls == ProjectPage:
        return ProjectPageForm
    return cls

@hooks.register('after_create_page')
@hooks.register('after_edit_page')
def handle_m2m_relationships(request, page):
    if isinstance(page, BlogPage):
        if hasattr(page, '_pending_technologies'):
            page.technologies.set(page._pending_technologies)
        if hasattr(page, '_pending_tags'):
            page.tags.set(page._pending_tags)
    elif isinstance(page, ProjectPage):
        if hasattr(page, '_pending_technologies'):
            page.technologies.set(page._pending_technologies)

@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != 'snippets']
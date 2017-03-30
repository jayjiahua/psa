from django.contrib import admin

# Register your models here.

from .models import Channel, News, NewsComment

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    search_fields = ['name']

admin.site.register(Channel, ChannelAdmin)


class CommentInline(admin.TabularInline):
    model = NewsComment
    extra = 0


class NewsAdmin(admin.ModelAdmin):
    list_display = ('news_id', 'title', 'interaction_count', 'comments_count', 'channel', 'publish_at')
    search_fields = ['title']
    list_filter = ['channel', 'publish_at']
    # inlines = [CommentInline]

admin.site.register(News, NewsAdmin)

class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'news', 'content', 'vote_count', 'against_count', 'is_anonymous')
    list_filter = ['province']

admin.site.register(NewsComment, NewsCommentAdmin)

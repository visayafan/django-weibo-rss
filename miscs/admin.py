from django.contrib import admin

from weibo.models import FeedModel


class FeedModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'link']


admin.site.register(FeedModel, FeedModelAdmin)

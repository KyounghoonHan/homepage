from django.contrib import admin

# Register your models here.
from .models import Post, Category, Tag, Comment

admin.site.register(Post)
admin.site.register(Comment)

class CategoryAdmin(admin.ModelAdmin):
    """ Fill in slug field automatically """
    prepopulated_fields = {'slug': ('name', )}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)

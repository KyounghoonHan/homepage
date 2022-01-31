from django.contrib import admin

# Register your models here.
from .models import Post, Category

admin.site.register(Post)

class CategoryAdmin(admin.ModelAdmin):
    """ Fill in slug field automatically """
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Category, CategoryAdmin)
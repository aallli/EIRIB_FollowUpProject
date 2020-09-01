from . import models
from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True


class SubCategoryInline(admin.TabularInline):
    model = models.SubCategory


@admin.register(models.SubCategory)
class SubCategoryAdmin(BaseModelAdmin):
    model = models.SubCategory
    list_display = ['category', 'name']
    list_display_links = ['category', 'name']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


@admin.register(models.Category)
class CategoryAdmin(BaseModelAdmin):
    model = models.Category
    search_fields = ['name', ]
    inlines = [SubCategoryInline]


@admin.register(models.Activity)
class ActivityAdmin(BaseModelAdmin):
    model = models.Activity
    search_fields = ['name', ]

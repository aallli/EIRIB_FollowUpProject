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


@admin.register(models.CommitteeMember)
class CommitteeMemberAdmin(BaseModelAdmin):
    model = models.CommitteeMember
    list_display = ['user', 'chairman']
    list_display_links = ['user', 'chairman']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']


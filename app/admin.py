from django.contrib import admin
from app.models import Request, UserProfile, Notification, RequestCategory, RequestSubCategory, SkillTag, Rating, Offer

admin.site.register(UserProfile)
admin.site.register(Notification)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "created")
    prepopulated_fields = {"slug": ("title",)}


class RequestCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class RequestSubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(RequestCategory, RequestCategoryAdmin)
admin.site.register(RequestSubCategory, RequestSubCategoryAdmin)
admin.site.register(SkillTag)
admin.site.register(Offer)
admin.site.register(Rating)
admin.site.register(Request, ProjectAdmin)

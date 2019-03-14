from django.contrib import admin
from honest.models import Category, Area, Person, UserProfile, Review


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category',)}


class AreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('state'),}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Area)
admin.site.register(Person)
admin.site.register(UserProfile)
admin.site.register(Review)
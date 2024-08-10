from django.contrib import admin
from core import models

# Register your models here.

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Connection)
class GroupAdmin(admin.ModelAdmin):
    pass

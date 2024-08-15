from django.contrib import admin
from core import models

# Register your models here.

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Connection)
class ConnectionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Expense)
class ExpenseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.SubExpense)
class SebExpenseAdmin(admin.ModelAdmin):
    pass
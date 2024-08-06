import json
from django.db import models

from splitfool.settings import BASE_DIR

# Create your models here.

class Currency(models.Model):
    pass

class Event(models.Model):
    title = models.CharField(max_length=100)
    begin_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(
        decimal_places=2
    )

class AbstractExpense(models.Model):
    with open( BASE_DIR / "core/ExpenseCategory.json", "r") as categroy_file:
        category_choices = json.load(categroy_file)
    # with open( BASE_DIR / "core/Currency.json", "r") as currency_file:
        # currency_choices = json.load(currency_file)
    currency_choices = [('01',('Dollar','$')),('02',('Iranian Rial', 'ریال'))]
    category = models.CharField(max_length=2, choices=category_choices)
    title = models.CharField(max_length=100)
    currency = models.CharField(max_length=2, choices=currency_choices)
    amount = models.DecimalField(
        decimal_places=2
    )

    class Meta:
        abstract = True


class Expense(AbstractExpense):
    pass

class SubExpense(AbstractExpense):
    parent_expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    parent_event = models.ForeignKey(Event, on_delete=models.CASCADE)



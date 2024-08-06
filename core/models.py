import json
import uuid
from django.db import models

from splitfool.settings import BASE_DIR

# Create your models here.

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)

class Group(models.Model):
    pass

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
        CATEGORY_CHOICES = json.load(categroy_file)
    # with open( BASE_DIR / "core/Currency.json", "r") as currency_file:
        # CURRENCY_CHOICES = json.load(currency_file)
    CURRENCY_CHOICES = [('01',('Dollar','$')),('02',('Iranian Rial', 'ریال'))]
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    currency = models.CharField(max_length=2, choices=CURRENCY_CHOICES, default='01')
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


class Connection(models.Model):
    GROUP_TYPE = ('G', 'Group')
    PERSONAL_TYPE = ('P', 'Personal')
    CONNECTION_TYPES = [GROUP_TYPE, PERSONAL_TYPE]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection_type = models.CharField(max_length=1, choices=CONNECTION_TYPES)
    first_side = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


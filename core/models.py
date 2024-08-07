import json
import uuid
from django.db import models
from django.contrib.auth.models import User
from splitfool.settings import BASE_DIR

# Create your models here.


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='own_groups', null=True)


class Connection(models.Model):
    GROUP_TYPE = 'g'
    PERSONAL_TYPE = 'p'
    CONNECTION_TYPES = [(GROUP_TYPE, 'Group'), (PERSONAL_TYPE, 'Personal')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection_type = models.CharField(max_length=1, choices=CONNECTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members', null=True)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', null=True)


class ConnectionInvitation(models.Model):
    PENDING_ = 'p'
    ACCEPTED_ = 'a'
    REJECTED_ = 'r'
    INVITATION_STATUS = [
        (PENDING_, 'Pending'),
        (ACCEPTED_, 'Accepted'),
        (REJECTED_, 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    invited = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_to')
    status = models.CharField(max_length=1, choices=INVITATION_STATUS, default=PENDING_)
    connection = models.OneToOneField(Connection, on_delete=models.CASCADE, null=True, related_name='invite')


class Currency(models.Model):
    pass

class Event(models.Model):
    title = models.CharField(max_length=100)
    begin_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    total_amount = models.DecimalField(
        max_digits=14,
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
        max_digits=14,
        decimal_places=2
    )

    class Meta:
        abstract = True


class Expense(AbstractExpense):
    pass


class SubExpense(AbstractExpense):
    parent_expense = models.ForeignKey(Expense, on_delete=models.CASCADE, null=True, related_name='subexpenses')
    parent_event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, related_name='subexpenses')



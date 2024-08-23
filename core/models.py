import json
import uuid

from django.db import models
from django.db.models.aggregates import Sum
from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.contrib.auth.models import User
from splitfool.settings import BASE_DIR

# Create your models here.


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='own_groups', null=True, blank=True)


class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections2')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_connection')
        ]


class ConnectionInvitation(models.Model):
    PENDING_ = 'p'
    ACCEPTED_ = 'a'
    REJECTED_ = 'r'
    INVITATION_STATUS = [
        (PENDING_, 'Pending'),
        (ACCEPTED_, 'Accepted'),
        (REJECTED_, 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invites')
    invited = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(max_length=1, choices=INVITATION_STATUS, default=PENDING_)
    connection = models.OneToOneField(Connection, on_delete=models.PROTECT, null=True, blank=True, related_name='invite')


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='memberships')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'user'], name='unique_membership')
        ]


class MembershipInvitation(models.Model):
    PENDING_ = 'p'
    ACCEPTED_ = 'a'
    REJECTED_ = 'r'
    INVITATION_STATUS = [
        (PENDING_, 'Pending'),
        (ACCEPTED_, 'Accepted'),
        (REJECTED_, 'Rejected'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invites')
    invited = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ginvitations')
    status = models.CharField(max_length=1, choices=INVITATION_STATUS, default=PENDING_)
    membership = models.OneToOneField(Membership, on_delete=models.PROTECT, null=True, blank=True, related_name='invite')


# class Currency(models.Model):
#     pass

class Event(models.Model):
    title = models.CharField(max_length=100)
    begin_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )


class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='events')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'user'], name='unique_Attendance')
        ]


class AbstractExpense(models.Model):
    with open( BASE_DIR / "core/ExpenseCategory.json", "r") as categroy_file:
        CATEGORY_CHOICES = json.load(categroy_file)
    # with open( BASE_DIR / "core/Currency.json", "r") as currency_file:
        # CURRENCY_CHOICES = json.load(currency_file)
    DOLLAR = '01'
    IRANIAN_RIALS = '02'
    CURRENCY_CHOICES = [(DOLLAR,'$'),(IRANIAN_RIALS, 'ریال')]

    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, blank=True, null=True)
    title = models.CharField(max_length=100)
    currency = models.CharField(max_length=2, choices=CURRENCY_CHOICES, default='01')
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    CONNECTION = 'c'
    GROUP = 'g'
    EXPENSE_TYPES = [
        (CONNECTION, 'Connection'),
        (GROUP, 'Group')
    ]
    expense_type = models.CharField(max_length=1, choices=EXPENSE_TYPES)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name='expenses')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expnses')

    def __str__(self) -> str:
        return self.title

    class Meta:
        abstract = True


class Expense(AbstractExpense):

    def calculate_amount(self):
        try:
            sub_expenses = SubExpense.objects.filter(parent_expense__id=self.id).aggregate(sub_total=Sum('amount'))
            if sub_expenses['sub_total'] != None:
                self.amount = sub_expenses['sub_total']
            print(sub_expenses)
        except ObjectDoesNotExist:
            return "Sub Expense does not exist"

    def save(self, **kwargs):
        self.calculate_amount()
        super().save(**kwargs)


class SubExpense(AbstractExpense):
    expense_type = None
    connection = None
    group = None
    parent_expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank=True, null=True, related_name='subexpenses')
    parent_event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True, related_name='subexpenses')

    def save(self, **kwargs):
        save_error = None
        save_message = f"Sub Expensed saved: {self.title}"
        if self.id:
            try:
                parent = Expense.objects.get(subexpenses=self.pk)
                # print('parent_expense')
                parent.save()
                super().save(**kwargs)
            except ObjectDoesNotExist:
                save_message = "No Parent Expense found\n"
                try:
                    parent = Event.objects.get(subexpenses=self.pk)
                    # print('parent_event')
                    parent.save()
                    super().save(**kwargs)
                except ObjectDoesNotExist:
                    save_message += "No Parent Event found\n"
                    save_error = f"Invalid SubExpense: {str(self)} , SubExpnese.id = {self.id}\n"
                    raise BadRequest(save_error + save_message)
            finally:
                print(save_message, f"self.id is: {self.id}")
                # super().save(**kwargs)
        elif (self.parent_expense is None and self.parent_event is None):
            save_error = f"Invalid SubExpense: {str(self)} , SubExpnese.id = {self.id}\n"
            save_message = f"No Parent Expense or Parent Event is selected"
            raise BadRequest(save_error + save_message)
        else:
            # print(self.parent_event, self.parent_expense)
            super().save(**kwargs)

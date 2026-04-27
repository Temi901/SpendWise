from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    CATEGORIES = [
        ('Food', 'Food'),
        ('Transport', 'Transport'),
        ('Housing', 'Housing'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('Clothing', 'Clothing'),
        ('Utilities', 'Utilities'),
        ('Savings', 'Savings'),
        ('Salary', 'Salary'),
        ('Freelance', 'Freelance'),
        ('Business', 'Business'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Budget(models.Model):
    CATEGORIES = [
        ('Food', 'Food'),
        ('Transport', 'Transport'),
        ('Housing', 'Housing'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('Clothing', 'Clothing'),
        ('Utilities', 'Utilities'),
        ('Savings', 'Savings'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()

    def __str__(self):
        return f"{self.category} - ₦{self.amount}"
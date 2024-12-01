from django.db import models
from django.contrib.auth import get_user_model

# Getting the auth user model
User = get_user_model()

class SimpleTransaction(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'p', 'Pending'
        SUCCESS = 's', 'Success'
        FAILED = 'f', 'Failed'

    class TransactionType(models.TextChoices):
        TOPUP = 't', 'TopUp'
        WITHDRAW = 'w', 'Withdraw'

    class PaymentMethod(models.TextChoices):
        KHALTI = "Khalti", "Khalti"
        ESEWA = 'Esewa', "Esewa"

    # Unique transaction identifier
    transaction_id = models.CharField(max_length=50, unique=True)

    # User accounts involved in the transaction
    account_number = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_transactions', to_field='account_number')

    # Balances before and after the transaction
    previous_balance = models.PositiveIntegerField()
    new_balance = models.PositiveIntegerField()

    # Transaction details
    amount_paid = models.PositiveIntegerField()  # Real money amount paid
    coins_amount = models.PositiveIntegerField()  # ManduCoins given

    status = models.CharField(choices=StatusChoices.choices, max_length=1)
    payment_method = models.CharField(choices=PaymentMethod.choices, max_length=7)

    # Timestamp of when the transaction was created and updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional reference ID for external tracking
    reference_id = models.CharField(max_length=100, null=True, blank=True)

    #Payment Method
    transaction_type = models.CharField(choices=TransactionType.choices, max_length=1)

    class Meta:
        indexes = [
            models.Index(fields=['account_number']),  # Index on the user (account_number)
        ]
        ordering = ['-created_at']  # Orders by latest 'created_at'

    def __str__(self):
        return f'Transaction {self.transaction_id}: {self.transaction_type} - {self.status}'
    
class TransferTransaction(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'p', 'Pending'
        SUCCESS = 's', 'Success'
        FAILED = 'f', 'Failed'

    # Unique transaction identifier
    transaction_id = models.CharField(max_length=50, unique=True)

    # User accounts involved in the transfer using 'account_number' as a reference
    sender_account_number = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions', to_field='account_number')
    receiver_account_number = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions', to_field='account_number')

    # Balances before and after the transaction for both sender and receiver
    sender_previous_balance = models.PositiveIntegerField()
    receiver_previous_balance = models.PositiveIntegerField()
    sender_new_balance = models.PositiveIntegerField()
    receiver_new_balance = models.PositiveIntegerField()

    # Amount transferred and transaction fee (charge)
    amount_transferred = models.PositiveIntegerField()
    charge = models.PositiveIntegerField()  # Fee/charge for the transaction

    # Transaction status
    status = models.CharField(choices=StatusChoices.choices, max_length=1)

    # Timestamps for when the transaction was created and updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional reference ID for external tracking
    reference_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['sender_account_number']),  # Index for faster lookups by sender
            models.Index(fields=['receiver_account_number']),  # Index for faster lookups by receiver
        ]
        ordering = ['-created_at']  # Orders by latest 'created_at'
        
    def __str__(self):
        return f'Transaction {self.transaction_id}: Transfer from {self.sender_account_number} to {self.receiver_account_number} - {self.status}'
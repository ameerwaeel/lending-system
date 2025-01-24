from celery import shared_task
from loan_app.models import Payment, Borrower
from django.core.exceptions import ObjectDoesNotExist

@shared_task
def process_payments_every_hour():
    pending_payments = Payment.objects.filter(is_paid=False)

    for payment in pending_payments:
        try:
            borrower = Borrower.objects.get(user=payment.loan.borrower.user)
        except ObjectDoesNotExist:
            continue  

        if borrower.balance >= payment.amount:
            borrower.balance -= payment.amount
            borrower.save()
            payment.is_paid = True
            payment.save()


            if all(p.is_paid for p in payment.loan.payments.all()):
                payment.loan.status = 'completed'
                payment.loan.save()
from celery import shared_task
from loan_app.models import Payment, Borrower
from django.core.exceptions import ObjectDoesNotExist

@shared_task
def process_payment_task(payment_id, user_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        borrower = Borrower.objects.get(user_id=user_id)

        if borrower.balance < payment.amount:
            return {"error": "Insufficient balance."}

        borrower.balance -= payment.amount
        borrower.save()

        payment.is_paid = True
        payment.save()

        if all(p.is_paid for p in payment.loan.payments.all()):
            payment.loan.status = 'completed'
            payment.loan.save()

        return {"success": "Payment processed successfully."}

    except Payment.DoesNotExist:
        return {"error": "Payment not found."}
    except Borrower.DoesNotExist:
        return {"error": "Borrower not found."}

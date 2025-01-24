from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(Borrower)    
admin.site.register(Lender)
admin.site.register(Loan)
admin.site.register(Payment)
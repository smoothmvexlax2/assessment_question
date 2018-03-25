from assessment_code import CreditCard
from datetime import date,timedelta


def test1():
    creditCard = CreditCard(35, 1000)
    creditCard.swipe(500.0)
    fake_date = date.today()+timedelta(days=35)
    print(creditCard.getCurrentBalance(fake_today=fake_date))

def test2():
    creditCard = CreditCard(0.35, 1000.00)  
    creditCard.swipe(500.0)
    fake_date1 = date.today()+timedelta(days=15)
    creditCard.makePayment(200, fake_today=fake_date1)
    fake_date2 = date.today()+timedelta(days=25)
    creditCard.swipe(100.0, fake_today=fake_date2)
    fake_date3 = date.today()+timedelta(days=31)
    print(creditCard.getCurrentBalance(fake_today=fake_date3))
    print(creditCard.getPaymentHistory)
    print(creditCard.getPurchaseHistory)



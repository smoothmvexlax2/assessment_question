from datetime import date, datetime, time, timedelta
import uuid

DAYS30 = timedelta(days=30)

class CreditCard:
    def __init__(self, cc_apr, cc_limit):
        #apr can be in decimal form or whole number for percent
        if cc_apr>1:
            cc_apr /=100.0
        self.apr= cc_apr
        self.account = Account(self.apr)
        self.creditLimit = round(float(cc_limit),2)
        self.active = True
        #incase of deactivation
    
    def swipe(self, amount, fake_today=None):
        self.account.checkPeriod(fake_today=fake_today)
        amount = float(amount)
        if (self.getCurrentBalance() + amount)> self.creditLimit:
            #this will decline the transaction with no transaction made
            return 
        self.account.chargeMade(amount, fake_today=fake_today)
        
    def makePayment(self, amount, fake_today=None):
        amount = float(amount)
        self.account.checkPeriod(fake_today=fake_today)
        #one can have a credit with their account
        self.account.paymentMade(amount, fake_today=fake_today)
    
    def getCurrentBalance(self, fake_today=None):
        self.account.checkPeriod(fake_today=fake_today)
        return self.account.outstandingBalance
    
    def getPaymentHistory(self):
        # dictionary with key as payment_x
        #where x is some positive integer
        return self.account.paymentHistory
    
    def getPurchaseHistory(self):
        # dictionary with key as charge_x
        #where x is some positive integer
        return self.account.chargeHistory

class Account:
    #credit card is attached to an account
    def __init__(self, apr):
        self.id = uuid.uuid1()
        self.activationDate = date.today()
        self.time = datetime.time(datetime.now())
        self.outstandingBalance = 0.0
        self.paymentHistory = {}
        self.chargeHistory = {}
        self.lastInterest = self.activationDate
        periodEndDate = self.activationDate + timedelta(days=30)
        self.periods = [Period(0.0, periodEndDate)]
        self.currentPeriod = self.periods[-1]
        self.dailyApr = apr/365
    
    
    def __str__(self):
        return "Account: {} \n Balance: ${} \n Period ends: {}".format(
                self.id,
                self.outstandingBalance,
                self.currentPeriod.periodEndDate,
                )
    
    def balanceAfterDayX(self, number):
        goalDate = self.activationDate + timedelta(days=number) 
        index = 0
        period = self.periods[number%30]
        balance = period.startingBalance
        while period.transactions[index].date<goalDate:
            action = period.transactions[index]
            if type(action) is AccountPayment:
                balance -= action.amount
            
            else:
                balance += action.amount
                
            index +=1
        return balance    
        
    def paymentMade(self, amount, fake_today=None):
        amount = round(amount,2)
        transactions = len(self.paymentHistory.keys())+1
        payment = AccountPayment(amount, fake_today=fake_today)
        self.paymentHistory['payment_'+str(transactions)] = payment
        self.currentPeriod.addTransaction(payment)
        self.outstandingBalance -= amount
    
    def chargeMade(self, amount, fake_today=None):
        amount = round(amount,2)
        transactions = len(self.chargeHistory.keys())+1
        charge = CardCharge(amount, fake_today=fake_today)
        self.chargeHistory['charge_'+str(transactions)] = charge
        self.currentPeriod.addTransaction(charge)
        self.outstandingBalance += amount
 
    def needNewId(self):
        #incase of repeat id
        self.id = uuid
    
    def checkPeriod(self, fake_today=None):
        today = date.today() if not fake_today else fake_today
        endOfPeriod = self.currentPeriod.periodEndDate
        if today > endOfPeriod:
            self.calcPeriodInterest()
            newEnd = endOfPeriod + DAYS30
            balance = self.outstandingBalance
            self.periods.append(Period(newEnd,balance))
    
    def calcPeriodInterest(self):
        index = 0 
        period = self.currentPeriod
        startingBalance = period.startingBalance
        startDate = period.periodEndDate - DAYS30
        transactions = period.transactions
        interest = period.interest
        while index<len(transactions):
            datelapse = transactions[index].date
            delta =  (datelapse - startDate).days
            amounts = 0
            interest += round((self.dailyApr *delta)*startingBalance, 2)
            while index<len(transactions) and ( 
                transactions[index].date == datelapse):
                action = transactions[index]

                if type(action) is AccountPayment:
                    amounts -= action.amount
            
                else:
                    amounts += action.amount
                index +=1
            
            startingBalance += round(amounts,2)

            startDate += timedelta(days=delta)
        #calculate last days of inactivity ----below----

        remainingDays = (period.periodEndDate - startDate).days
        interest +=round((self.dailyApr *remainingDays)*startingBalance,2)
        self.outstandingBalance += interest
        
       
class CardCharge:
    def __init__(self, amount, fake_today=None):
        self.amount = amount
        self.approved = True
        self.date = date.today() if not fake_today else fake_today
        self.time = datetime.time(datetime.now())
    
    def __str__(self):
        return "Amount Charged: ${} \n On {} \n ".format(
                self.amount,
                self.date,
                )
        
class AccountPayment:
    def __init__(self, amount, fake_today=None):
        self.amount = amount
        self.date = date.today() if not fake_today else fake_today
        self.time = datetime.time(datetime.now())
    
    def __str__(self):
        return "Amount Payed: ${} \n On {} \n ".format(
                self.amount,
                self.date,
                )
                       
class Period:
    def __init__(self, starting_balance, the_date):
        self.startingBalance = starting_balance
        self.periodEndDate = the_date
        self.transactions = []
        self.interest = 0.0
       
        
    def addTransaction(self, transaction):
        if type(transaction) is AccountPayment or CardCharge:
        #transactions will be of CardCharge class or AccountPayment class
            self.transactions.append(transaction)
            

    def __str__(self):
        return "Period End Date: {} \n Number of transactions so far: {} \n ".format(
                self.periodEndDate,
                len(self.transactions),
                )


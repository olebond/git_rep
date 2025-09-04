class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner 
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Added: {amount} to the balance")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Not enough balance")
        else:
            self.balance = self.balance - amount
            print(f"Withdrawal accepted: {amount}")

    def __str__(self):
        return f"Account owner: {self.owner}\nAccount balance: {self.balance}"
    
def main():
    acct1 = Account('Jose', 100)
    print(acct1)
    acct1.deposit(50)
    print(acct1)
    acct1.withdraw(75)
    print(acct1)
    acct1.withdraw(500)
    print(acct1)

if __name__ == "__main__":
    main()
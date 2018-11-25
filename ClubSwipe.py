# ClubScanner
# A program to track glee attendence and payments using Pitt ID scanning
# Begun on August 9th, 2018 by Pat Healy

import pickle
import datetime
import os.path
       
class Rehearsal:
    def __init__(self, nm):
        self.name = nm
        self.attendees = []
        self.lates = []
        self.very_lates = []
        self.exempt = []
        
    def add_attendee(self, attendee, tp):
        "Given user attended rehearsal"
        if tp == "late":
            self.lates.append(attendee)
        elif tp == "very-late":
            self.very_lates.append(attendee)
        else:
            self.attendees.append(attendee)
        
    def add_exempt(self, attendee):
        "Given user is exempt from attendance"
        self.exempt.append(attendee)

class Payment:
    def __init__(self, nm, total):
        self.name = nm
        self.total = total
        self.payers = {}

    def pay(self, nm, amount):
        "Given user pays given amount"
        if nm not in self.payers.keys():
            self.payers[nm] = amount
        else:
            self.payers[nm] = str(int(self.payers[nm]) + int(amount))
        
    def pay_full(self, nm):
        "Given user pays in full"
        self.payers[nm] = self.total
        
    def exempt(self, nm):
        "Given user is exempt from payment"
        self.payers[nm] = "EXEMPT"
    
class GleeScanner:
    def __init__(self):
        "Init database; load from file if present"
        
        self.members = {}
        self.sections = {}
        self.sections['T1'] = []
        self.sections['T2'] = []
        self.sections['Bari'] = []
        self.sections['Bass'] = []
        self.payments = []
        self.rehearsals = []
        
        if os.path.isfile("glee_data"):
            self.load()
        else:
            print("Instantiated new database")
        
    def load(self):
        "Loads data from pickle file"
        # open a file, where you stored the pickled data
        file = open('glee_data', 'rb')

        # dump information to that file
        stuff = pickle.load(file)
        self.members = stuff['members']
        self.sections = stuff['sections']
        self.payments = stuff['payments']
        self.rehearsals = stuff['rehearsals']

        # close the file
        file.close()
        
        print("Loaded from file")
        
    def save_data(self):
        "Saves data to pickle file"
        stuff = {}
        stuff['members'] = self.members
        stuff['sections'] = self.sections
        stuff['payments'] = self.payments
        stuff['rehearsals'] = self.rehearsals
        
        outFile = open("glee_data", "wb")
        pickle.dump(stuff, outFile)
        outFile.close()
        
    def save(self):
        "Calls save data and saves to csv"
        
        self.save_data()
        
        header = "Name, Section"
        
        for p in self.payments:
            header = header + ", " + p.name
        
        for r in self.rehearsals:
            header = header + ", " + r.name
        
        header = header + ", Total Absences\n"
        
        spreadFileName = "GleeSpreadsheet_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + ".csv"
        
        spreadFile = open(spreadFileName, "w")
        spreadFile.write(header)
        
        for sect in self.sections:
            for c in self.sections[sect]:
                nm = self.members[c]
                line = "" + nm + ", " + sect
                
                for p in self.payments:
                    if nm not in p.payers.keys():
                        line = line + ", 0"
                    else:
                        if p.payers[nm] == "EXEMPT" or p.payers[nm] == "exempt":
                            line = line + ", " + "EXEMPT"
                        elif int(p.payers[nm]) >= int(p.total):
                            line = line + ", PAID"
                        else:
                            line = line + ", " + p.payers[nm]
                
                absences = 0
                for r in self.rehearsals:
                    if nm in r.attendees:
                        line = line + ", PRESENT"
                    elif nm in r.exempt:
                        line = line + ", EXCUSED"
                    elif nm in r.lates:
                        line = line + ", LATE"
                    elif nm in r.very_lates:
                        line = line + ", VERY LATE"
                    else:
                        line = line + ", ABSENT"
                        absences = absences + 1
                
                line = line + ", " + str(absences)
                
                line = line + "\n"
                spreadFile.write(line)
        
        spreadFile.close()
        print("Output to " + spreadFileName)
        
    def add_new_members(self):
        "Add new members to database, using swiped card"
        sections_type = ["T1", "T2", "Bari", "Bass"]
        print("Type 'done' when finished")

        nm = str(input("Name: "))
        while not nm == "done":
            section = input("Section: ")
            while not (section in sections_type):
                print("ERROR xxxxx Not a valid section name")
                section = input("Section (T1, T2, Bari, or Bass): ")
            card = input("Swipe Card: ")
            self.sections[section].append(card)
            self.members[card] = nm
            print("Added " + nm)
            nm = input("Name: ")
    
    def add_new_rehearsal(self):
        "Create a new rehearsal"
        rname = input("Name for the new rehearsal: ")
        
        found = False
        for r in self.rehearsals:
            if rname == r.name:
                found = True
        
        while(found):
            print("Name already taken.")
            rname = input("Unique name for the new rehearsal: ")
        
            found = False
            for r in self.rehearsals:
                if rname == r.name:
                    found = True
        
        rehearse = Rehearsal(rname)
        self.rehearsals.append(rehearse)
        print("Added rehearsal " + rname)
        
        self.swipe_in(len(self.rehearsals)-1)
        
    def swipe_in(self, rehearseIndex):
        "Swiped in users are present at a specific rehearsal"
        rehearse = self.rehearsals[rehearseIndex]
        print("Type 'done' when finished")
        
        tp = "present"
        card = input("Card: ")
        while not card == "done":
            if card == "late":
                tp = "late"
                print("Swipe in late attendees")
            elif card == "very-late":
                tp = "very late"
                print("Swipe in very late attendees")
            elif card == "present":
                tp = "present"
                print("Swipe in on-time attendees")
            elif(card in self.members.keys()):
                rehearse.add_attendee(self.members[card], tp)
                print(self.members[card] + " was " + tp + " at " + rehearse.name)
            else:
                print("ERROR XXXXXX Card not in registry")
            card = input("Card: ")
        
        self.rehearsals[rehearseIndex] = rehearse

    def rehearsal_log(self, rehearseIndex):
        "Named users are present at a specific rehearsal"
        rehearse = self.rehearsals[rehearseIndex]
        print("Type 'done' when finished")
        
        card = input("Name: ")
        while not card == "done":
            if(card in self.members.values()):
                rehearse.add_attendee(card)
                print(card + " was present at " + rehearse.name)
            else:
                print("ERROR XXXXXX Name not in registry")
            card = input("Name: ")
        
        self.rehearsals[rehearseIndex] = rehearse
    def rehearsal_except(self, rehearseIndex):
        "Exempt given users from specific rehearsal attendance"
        rehearse = self.rehearsals[rehearseIndex]
        print("Type 'done' when finished")
        
        card = input("Name: ")
        while not card == "done":
            if(card in self.members.values()):
                rehearse.add_exempt(card)
                print(card + " is now excused from " + rehearse.name)
            else:
                print("ERROR XXXXXX Card not in registry")
            card = input("Name: ")
        
        self.rehearsals[rehearseIndex] = rehearse
        
    def add_new_payments(self):
        "Create a new payment event to add member payments to; automatically asks for users to swipe payments in full"
        pname = input("Name for the new payment: ")
        
        found = False
        for p in self.payments:
            if pname == p.name:
                found = True
        
        while(found):
            print("Name already taken.")
            pname = input("Unique name for the new payment: ")
        
            found = False
            for p in self.payments:
                if pname == p.name:
                    found = True
        
        total = float(input("How much will it cost? (Number): "))
        
        payment = Payment(pname, total)
        self.payments.append(payment)
        print("Added payment " + pname)
        
        self.swipe_pay_full(len(self.payments)-1)
    
    def swipe_pay_full(self, paymentIndex):
        "Swiped in users have paid in full"
        payment = self.payments[paymentIndex]
        print("Swipe a card to have them pay in full for " + payment.name)
        print("Type 'done' when finished")
        
        card = input("Card: ")
        while not card == "done":
            if(card in self.members.keys()):
                payment.pay_full(self.members[card])
                print(self.members[card] + " has paid in full for " + payment.name)
            else:
                print("ERROR XXXXXX Card not in registry")
            card = input("Card: ")
        
        self.payments[paymentIndex] = payment
        
    def log_pay_full(self, paymentIndex):
        "Named users have paid in full"
        payment = self.payments[paymentIndex]
        print("Name a member to have them pay in full for " + payment.name)
        print("Type 'done' when finished")
        
        card = input("Name: ")
        while not card == "done":
            if(card in self.members.values()):
                payment.pay_full(card)
                print(card + " has paid in full for " + payment.name)
            else:
                print("ERROR XXXXXX Name not in registry")
            card = input("Name: ")
        
        self.payments[paymentIndex] = payment
    
    def payment_except(self, paymentIndex):
        "Exempt given users from a specific payment"
        payment = self.payments[paymentIndex]
        print("Type a name to have them exempt for " + payment.name)
        print("Type 'done' when finished")
        
        card = input("Name: ")
        while not card == "done":
            if(card in self.members.values()):
                payment.exempt(card)
                print(card + " is exempt for " + payment.name)
            else:
                print("ERROR XXXXXX Card not in registry")
            card = input("Name: ")
        
    def partial_payment(self, paymentIndex):
        "Add given partial payments to given users on a specific payment"
        payment = self.payments[paymentIndex]
        print("Swipe a card to have them pay in full for " + payment.name)
        print("Type 'done' when finished")
        
        card = input("Name: ")
        while not card == "done":
            if(card in self.members.values()):
                amount = input("Payment amount: ")
                payment.pay(card, amount)
                print(card + " paid " + amount + ", totaling " + payment.payers[card])
            else:
                print("ERROR XXXXXX Card not in registry")
            card = input("Name: ")
        
    def modify_rehearsal(self):
        "Menu to modify an existing rehearsal; making changes to member attendance statuses"
        print("What do you want to do?")
        print("\t1. Swipe into rehearsal")
        print("\t2. Add exeptions by Name")
        print("\t3. Add attendence by Name")
        
        cat1 = str(input("~: "))
        
        while not (cat1 == "1" or cat1 == "2" or cat1 == "3"):
            cat1 = str(input("~: "))
        
        print("Choose a rehearsal by number: ")
        for i in range(len(self.rehearsals)):
            print("\t" + str(i+1) + ". " + self.rehearsals[i].name)
        
        cat2 = int(input("~: ")) - 1
        
        if cat1 == "1":
            self.swipe_in(cat2)
        elif cat1 == "2":
            self.rehearsal_except(cat2)
        else:
            self.rehearsal_log(cat2)
        
        
    def modify_payment(self):
        "Menu to modify an existing payment; making changes to member payment statuses"
        print("What do you want to do?")
        print("\t1. Swipe to pay in full")
        print("\t2. Add exeptions by Name")
        print("\t3. Add partial payment by Name")
        print("\t4. Pay in full by Name")
        
        cat1 = str(input("~: "))
        
        while not (cat1 == "1" or cat1 == "2" or cat1 == "3" or cat1 == "4"):
            cat1 = str(input("~: "))
        
        print("Choose a payment by number: ")
        for i in range(len(self.payments)):
            print("\t" + str(i+1) + ". " + self.payments[i].name)
        
        cat2 = int(input("~: ")) - 1
        
        if cat1 == "1":
            self.swipe_pay_full(cat2)
        elif cat1 == "2":
            self.payment_except(cat2)
        elif cat1 == "3":
            self.partial_payment(cat2)
        else:
            self.log_pay_full(cat2)
        
    def main_menu(self):
        "Main menu of the application where users can choose what to do next"
        print("Here's stuff you can do:")
        print("\t1. Add New Members")
        print("\t2. Add a New Rehearsal")
        print("\t3. Add a New Payment")
        print("\t4. Modify an existing Rehearsal")
        print("\t5. Modify an existing Payment")
        print("\t6. Save and Quit")
        
        try: 
            choice = str(input("~: "))

            end = False

            if choice == "1":
                self.add_new_members()
            elif choice == "2":
                self.add_new_rehearsal()
            elif choice == "3":
                self.add_new_payments()
            elif choice == "4":
                self.modify_rehearsal()
            elif choice == "5":
                self.modify_payment()
            elif choice == "6":
                self.save()
                end = True
            else:
                print("Invalid input.")

            self.save_data()

            if not end:
                self.main_menu()
        
        except:
            print("ERROR XXX Runtime Exception")
            self.save_data()
            self.main_menu()
        
if __name__ == "__main__":
    print("")
    print("ClubSwipe by Pat Healy")
    print("===========================================")
    print("$$$$$$$\\  $$\\      $$\\  $$$$$$\\   $$$$$$\\")  
    print("$$  __$$\\ $$$\\    $$$ |$$  __$$\\ $$  __$$\\") 
    print("$$ |  $$ |$$$$\\  $$$$ |$$ /  \\__|$$ /  \\__|")
    print("$$$$$$$  |$$\\$$\\$$ $$ |$$ |$$$$\\ $$ |")      
    print("$$  ____/ $$ \\$$$  $$ |$$ |\\_$$ |$$ |")      
    print("$$ |      $$ |\\$  /$$ |$$ |  $$ |$$ |  $$\\") 
    print("$$ |      $$ | \\_/ $$ |\\$$$$$$  |\\$$$$$$  |")
    print("\\__|      \\__|     \\__| \\______/  \\______/")
    print("===========================================")
    
    scanner = GleeScanner()
    scanner.main_menu()
    
import sys
from pymongo import MongoClient

col = None
positions = ["GK", "RB", "RCB", "CB", "LCB", "LB", "RWB", "RDM", "CDM", "LDM", "LWB", "RM", "RCM", "CM", "LCM", "LM", "RAM", "CAM", "LAM", "RW", "RF", "CF", "LF", "LW", "RS", "ST", "LS"]

# Print user menu options
def printMenuOptions():
    print("\n--- CS432 FIFA 19 Analyzer ---")
    print("1: Get highest rated player(s)")
    print("2: Get number of right-footed vs. left-footed players")
    print("3: Get the highest paid player at each position")
    print("4: Get the highest paid player at a specific position")
    print("5: Get the club with the highest average player rating in the world")
    print("7: Quit Program\n")

# Handle user's input
def handleUserInput(menuChoice):
    global col

    if menuChoice == 1: getHighestRated()
    elif menuChoice == 2: getNumFooted()
    elif menuChoice == 3: getHighestPaid()
    elif menuChoice == 4:
        pos = input("Please enter a position: ")
        print()
        getHighestPaidAtPosition(pos)
    elif menuChoice == 5: getHighestRatedTeam()
    elif menuChoice == 7: sys.exit(0)
    else: print("Please choose a valid option.")

# Get the highest rated player(s) in FIFA 19
def getHighestRated():
    global col

    res = col.find(sort=[("Overall", -1)])
    overall = 0
    for x in res:
        ovr = int(x["Overall"])
        if ovr >= overall:
            overall = ovr
            print(x["Name"] + " " + x["Overall"])
        else: break

# Get the number and percentage of each type of foot preference
def getNumFooted():
    global col

    right = col.count_documents({"Preferred Foot" : "Right"})
    left = col.count_documents({"Preferred Foot" : "Left"})
    na = col.count_documents({"Preferred Foot" : ""})
    total = col.count_documents({})

    print("Total Number of Players:\t" + str(total))
    print("Right-Footed Players:\t\t" + str(right))
    print("Left-Footed Players:\t\t" + str(left))
    print("Preferred Foot Not Specified:\t" + str(na) + "\n")

    pctRight = round((right / total) * 100, 2)
    pctLeft = round((left / total) * 100, 2)
    pctNA = round((na / total) * 100, 2)

    print("Right-Footed Players Percentage:\t" + str(pctRight) + "%")
    print("Left-Footed Players Percentage:\t\t" + str(pctLeft) + "%")
    print("Preferred Foot Not Specified Percentage: " + str(pctNA) + "%")

# Get the highest paid player at a specific position
def getHighestPaidAtPosition(pos):
    global col
    global positions

    if pos not in positions:
        print("Position does not exist.")
        return

    res = col.find({"Position" : pos})

    playerName = ""
    highestSalary = 0
    for x in res:
        val = str(x["Value"])
        tempSalary = val[1:]
        salary = 0
        if "M" in tempSalary:
            salary = float(tempSalary[:-1]) * 1000000
        elif "K" in tempSalary:
            salary = float(tempSalary[:-1]) * 1000

        if salary > highestSalary:
            playerName = x["Name"]
            highestSalary = salary

    print(pos + ": " + playerName + " €" + "{:,.2f}".format(round(highestSalary,2)))

# Get the highest paid player at each position
def getHighestPaid():
    global positions
    for pos in positions:
        getHighestPaidAtPosition(pos)

# Get the highest rated team in the world
def getHighestRatedTeam():
    global col

    # Get all players that have a club and sort them by club
    res = col.find({"Club" : { "$ne" : ""}}).sort("Club")

    currClub = res[0]["Club"]
    rating = 0
    numPlayers = 0

    bestAvg = 0
    bestTeam = None

    for x in res:
        if(x["Club"] != currClub):
            avg = round(rating / numPlayers, 2)

            if avg > bestAvg:
                bestAvg = avg
                bestTeam = currClub

            currClub = x["Club"]
            rating = 0
            numPlayers = 0

        rating += int(x["Overall"])
        numPlayers += 1

    print("The club with the highest rated team is " + bestTeam + " with an average rating of " + str(bestAvg) + "!")

def main():
    global col

    # Retrieve username and password from file
    fileIn = open('connect.txt', 'r')
    login = fileIn.readlines()
    username = login[0].strip()
    password = login[1].strip()
    fileIn.close()

    # Create MongoDB connection
    while(True):
        try:
            client = MongoClient("mongodb+srv://" + username + ":" + password + "@cluster0-3fgun.mongodb.net/test?retryWrites=true&w=majority")
            break
        except: continue

    db = client.fifa    # Access database
    col = db.players    # Access collection

    print("\nWelcome " + username + "!")

    while(True):
        printMenuOptions()

        try:
            # Retrieve user input
            menuChoice = int(input("Please enter a numeric choice: "))
            print()
        except:
            # Pass invalid option to handler
            menuChoice = -1

        handleUserInput(menuChoice)

main()

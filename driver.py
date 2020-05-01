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
    print("5: Get the clubs with the highest average player rating in the world")
    print("6: Get the nations with the highest average potential rating")
    print("7: Quit Program\n")

# Handle user's input
def handleUserInput(menuChoice):
    global col

    # Call function based on user input
    if menuChoice == 1: getHighestRated()
    elif menuChoice == 2: getNumFooted()
    elif menuChoice == 3: getHighestPaid()
    elif menuChoice == 4:
        pos = input("Please enter a position: ")
        print()
        getHighestPaidAtPosition(pos)
    elif menuChoice == 5:
        while(True):
            try:
                nClubs = int(input("Please enter a number of clubs: "))
                break
            except: continue
        print()
        getHighestRatedClubs(nClubs)
    elif menuChoice == 6:
        while(True):
            try:
                nNations = int(input("Please enter a number of nations: "))
                break
            except: continue
        print()
        getHighestPotentialNations(nNations)
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

    # Get number of each foot preference
    right = col.count_documents({"Preferred Foot" : "Right"})
    left = col.count_documents({"Preferred Foot" : "Left"})
    na = col.count_documents({"Preferred Foot" : ""})
    total = col.count_documents({})

    print("Total Number of Players:\t" + str(total))
    print("Right-Footed Players:\t\t" + str(right))
    print("Left-Footed Players:\t\t" + str(left))
    print("Preferred Foot Not Specified:\t" + str(na) + "\n")

    # Calculate percentages
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

    # Check if position exists
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

        # Convert abbreviated form to int form
        if "M" in tempSalary:
            salary = float(tempSalary[:-1]) * 1000000
        elif "K" in tempSalary:
            salary = float(tempSalary[:-1]) * 1000

        # Check if current salary is greater than the current highest
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
def getHighestRatedClubs(nClubs):
    global col

    clubs = []

    print("Top " + str(nClubs) + " clubs with the highest average player rating:")

    for i in range(0, nClubs):
        # Get all players that have a club and sort them by club
        res = col.find({"Club" : { "$ne" : ""}}).sort("Club")

        currClub = res[0]["Club"]
        rating = 0
        numPlayers = 0

        bestAvg = 0
        bestClub = None

        for x in res:
            # If nation already counted skip
            if(x["Club"] in clubs): continue

            # Check if end of a specific club
            if(x["Club"] != currClub):
                avg = round(rating / numPlayers, 2)

                # Check if club has better rating than the current best club
                if avg > bestAvg:
                    bestAvg = avg
                    bestClub = currClub

                # Reset values for new club
                currClub = x["Club"]
                rating = 0
                numPlayers = 0

            rating += int(x["Overall"])
            numPlayers += 1

        # Account for last team
        avg = round(rating / numPlayers, 2)

        if avg > bestAvg:
            bestAvg = avg
            bestClub = currClub

        # Add current best rated club to list of clubs
        clubs.append(bestClub)

        print(str(i+1) + ". " + bestClub + " with an average rating of " + str(bestAvg))

# Get the nations with the highest average potential
def getHighestPotentialNations(nNations):
    global col

    nations = []

    print("Top " + str(nNations) + " nations with the highest average potential:")

    for i in range(0, nNations):
        # Get all players and sort them by nationality
        res = col.find().sort("Nationality")

        currNation = res[0]["Nationality"]
        potential = 0
        numPlayers = 0
        currBest = None
        bestAvg = 0

        for x in res:
            # If nation already counted skip
            if(x["Nationality"] in nations): continue

            # Check if end of a specific nation
            if(x["Nationality"] != currNation):
                avg = round(potential / numPlayers, 2)

                # Check if nation has better rating than the current best
                if avg > bestAvg:
                    bestAvg = avg
                    currBest = currNation

                # Reset values for new nation
                currNation = x["Nationality"]
                potential = 0
                numPlayers = 0

            potential += int(x["Potential"])
            numPlayers += 1

        # Account for last nation
        avg = round(potential / numPlayers, 2)

        if avg > bestAvg:
            bestAvg = avg
            currBest = currNation

        # Add current best rated nation to list of nations
        nations.append(currBest)

        print(str(i+1) + ". " + currBest + " with a potential rating of " + str(bestAvg))

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

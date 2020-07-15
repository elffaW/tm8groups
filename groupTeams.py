import sys
import os
import csv
import statistics

BOT_VALUE = 3

def findBest(items, bins, maxBinSize):
    if len(items) < 2:
        return 0
    
    minIdx = 0
    minItem = 1000000
    i = 0
    while i < len(items):
        item = items[i]
        bin = bins[i]
        if item < minItem and len(bin) < maxBinSize:
            minItem = item
            minIdx = i
        i += 1
    
    return minIdx


# Function to extract frames 
# @param playersFile csv file of all players in player,value format
# @param teamSize int number of players per team
def CreateTeams(playersFile, teamSize):
    print("Creating teams from the following parameters")
    print("players file: {0}, team size: {1}, bot value: {2}".format(playersFile, teamSize, BOT_VALUE))
    
    with open(playersFile, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        playerValues = {}
        totalValue = 0
        curLine = 0
        for row in csv_reader:
            if curLine == 0:
                name = list(row.keys())[0]
                value = list(row.keys())[1]
                name = "Name"
                value = "Value"
                print(f'Column names are {", ".join(row)}')
                curLine += 1
            # print(f'\t{row[name]}\t is worth ${row[value]}M')
            playerValues.setdefault(row[name], float(row[value]))
            totalValue += float(row[value])
            curLine += 1
        curLine -= 1 # subtract last increment
        print(f'Total players: {curLine}')
        
        # add in bots (if needed)
        numBots = (teamSize - (curLine % teamSize)) % teamSize
        print(f'Need to add {numBots} bots (at value {BOT_VALUE}) for even teams.')
        botNum = 1
        while botNum <= numBots:
            playerValues.setdefault(f'BOT{botNum}', BOT_VALUE)
            botNum += 1
            totalValue += BOT_VALUE
        print(f'Player:Values {playerValues}')

        numTeams = int(len(playerValues) / teamSize)
        print(f'Num teams:\t{numTeams}\tNum players: {len(playerValues)}')

        avg = statistics.mean(playerValues.values())
        stdDev = statistics.pstdev(playerValues.values())
        print(f'Average:\t{avg}')
        print(f'Median :\t{statistics.median(playerValues.values())}')
        print(f'Quantiles:\t{statistics.quantiles(playerValues.values(), n=teamSize)}')
        print(f'Std Dev:\t{stdDev}')
        print(f'Total Value:\t{totalValue}')

        MAX_TEAM = (avg * 3) + (stdDev)
        MIN_TEAM = (avg * 3) - (stdDev)

        # initialize teams and their sums
        n = 0
        teams = []
        sums = []
        while n < numTeams:
            teams.append([])
            sums.append(0)
        #     i = 0
        #     s = 0
        #     tempValues = playerValues.copy()
        #     while s < teamSize and len(tempValues) > 0:
        #         p = list(tempValues)[0]
        #         v = tempValues[p]
        #         if sums[n] < MAX_TEAM and (sums[n] + v) < MAX_TEAM:
        #             teams[n].append({p, v})
        #             sums[n] += v
        #             s += 1
        #             playerValues.pop(p)

        #         tempValues.pop(p)

        #         if s == teamSize:
        #             break
            n += 1
        r = 0

        sortedPlayers = {k: v for k, v in sorted(playerValues.items(), reverse=True, key=lambda item: item[1])}

        for p, v in sortedPlayers.items():
            tempValues = playerValues.copy()
            if len(tempValues) > 0:
                minIdx = findBest(sums, teams, teamSize)
                print(f'minIdx: {minIdx}\tcurPlayer: {(p, v)}')
                if len(teams[minIdx]) < teamSize:
                    teams[minIdx].append((p, v))
                    sums[minIdx] += v
                    playerValues.pop(p)
            r += 1

        # print(f'players leftover: {playerValues}')

        t = 0
        while t < len(teams):
            # printing with commas so it's easier to paste into a spreadsheet
            print(f'TEAM {t},\t{sums[t]:.2f}')
            for p in teams[t]:
                print(f'\t,{p[0]},\t{p[1]}')
            t += 1

        print(f'Average:\t{statistics.mean(sums)}')
        print(f'Std Dev:\t{statistics.pstdev(sums)}')



def UsageError():
    print("USAGE: `python3 groupTeams.py <players> <teamSize> [botValue]`")
    print("PARAM players: string representing the path to the player value CSV file (with header row)")
    print("PARAM teamSize: integer representing the number of players per team")
    print("PARAM (optional) botValue: decimal number representing the value of bots if needed to pad teams. Defaults to 3")
    exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        UsageError()

    players = str(sys.argv[1])
    teamSize = int(sys.argv[2])

    if len(sys.argv) == 4:
        BOT_VALUE = float(sys.argv[3])
    
    # Calling the function 
    CreateTeams(players, teamSize)
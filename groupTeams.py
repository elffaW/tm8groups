import sys
import os
import csv
import statistics
import random
from itertools import islice

BOT_VALUE = 3

def findBest(items, bins, maxBinSize):
    """find the index of the "best bin" (the one with lowest value that still has room for more items)

        Arguments:
            items {list} of values
            bins {list} of bins with items in them
            maxBinSize {int} max number of items in a bin

        Returns:
            {int} - index into the items (and bins) array with the lowest value that has room for another item
    """

    if len(items) < 2:
        return 0
    
    minIdx = 0
    minItem = 1000000
    i = 0
    while i < len(items):
        item = items[i]
        bin = bins[i]
        if len(bin) < maxBinSize:
            if round(item, 1) == round(minItem, 1):
                print(f'item: {round(item,1)}|{len(bin)}\tminItem: {round(minItem,1)}|{len(bins[minIdx])}')
            
            if round(item, 1) < round(minItem, 1) or (round(item, 1) == round(minItem, 1) and len(bin) > len(bins[minIdx])):
                minItem = item
                minIdx = i
        i += 1
    
    return minIdx


def CreateTeams(playersFile, teamSize, randomTiered=False):
    """Reads players from the file and creates teams using a Best First bin-packing heuristic
        
        Arguments:
            -playersFile {string} csv file path of all players in player,value format
            -teamSize {int} number of players per team
            -randomTiered {bool} if true, assign teams using random-tiered approach instead of best-first
        
        Returns:
            N/A
    """

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
                # print(f'Column names are {", ".join(row)}')
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
        # print(f'Player:Values {playerValues}')

        numTeams = int(len(playerValues) / teamSize)
        print(f'Num teams:\t{numTeams}\tNum players: {len(playerValues)}')

        print('---------------------- Stats ----------------------')
        avg = statistics.mean(playerValues.values())
        stdDev = statistics.pstdev(playerValues.values())
        print(f'Average:\t{avg}')
        print(f'Median :\t{statistics.median(playerValues.values())}')
        print(f'Quantiles:\t{statistics.quantiles(playerValues.values(), n=teamSize)}')
        print(f'Std Dev:\t{stdDev}')
        print(f'Total Value:\t{totalValue}')
        print('---------------------- ----- ----------------------')

        # initialize teams and their sums
        n = 0
        teams = []
        sums = []
        while n < numTeams:
            teams.append([])
            sums.append(0)
            n += 1
        r = 0

        sortedPlayers = {k: v for k, v in sorted(playerValues.items(), reverse=True, key=lambda item: item[1])}
        sortedPlayerValues = sortedPlayers.values()

        if randomTiered:
            # allocate players to teams with a random-tiered approach
            # initialize tiers of sub-arrays
            j = 0
            tiers = []
            while j < teamSize:
                tiers.append([])
                j += 1
            j = 0
            while j < teamSize:
                # tiers[j] = sortedPlayers[(numTeams * j):(numTeams * j+1)]
                startIdx = numTeams * j
                endIdx = numTeams * (j+1)
                curTier = list(islice(sortedPlayers, startIdx, endIdx))
                for p, v in sortedPlayers.items():
                    if p in curTier:
                        tiers[j].append((p, v))
                print(f'TIER {j}:\t{tiers[j]}')
                j += 1
            # print(tiers)
            # allocate players to teams
            i = 0
            random.seed()
            while i < numTeams:
                t = 0
                while t < teamSize:
                    idx = random.randint(0, len(tiers[t])-1)
                    player = tiers[t][idx]
                    # print(f'TEAM {i}, PLAYER {t}:\t{player}')
                    # if len(teams[idx]) < teamSize:
                    teams[i].append(player)
                    sums[i] += player[1]
                    tiers[t].pop(idx)
                    t += 1
                i += 1
        else:
            # allocate players to teams with a best-first approach
            for p, v in sortedPlayers.items():
                tempValues = playerValues.copy()
                if len(tempValues) > 0:
                    minIdx = findBest(sums, teams, teamSize)
                    # print(f'minIdx: {minIdx}\tcurPlayer: {(p, v)}')
                    if len(teams[minIdx]) < teamSize:
                        teams[minIdx].append((p, v))
                        sums[minIdx] += v
                        playerValues.pop(p)
                r += 1

        # print(f'players leftover: {playerValues}')
        # print teams to console and log to csv
        LogTeams(teams, sums)


def LogTeams(teams, sums):
    """ write teams to teams.csv file (and also print to console)
    """
    with open('teams.csv', 'w', newline='') as csvOut:
        fieldnames = ['TEAM', 'PLAYER', 'VALUE']
        csv_writer = csv.DictWriter(csvOut, fieldnames=fieldnames)
        csv_writer.writeheader()
            
        t = 0
        while t < len(teams):
            # printing with commas so it's easier to paste into a spreadsheet
            print(f'TEAM {t+1},\t{sums[t]:.2f},')
            teamName = "TEAM {0}".format(t+1)
            teamValue = str('{:.2f}').format(sums[t])
            csv_writer.writerow({'TEAM': teamName, 'PLAYER': teamValue, 'VALUE': ''})
            for p in teams[t]:
                print(f'\t,{p[0]},\t{p[1]:.1f}')
                playerName = p[0]
                playerValue = str('{:.1f}').format(p[1])
                csv_writer.writerow({'TEAM': '', 'PLAYER': playerName, 'VALUE': playerValue})
            t += 1
        
        csv_writer.writerow({ 'TEAM': 'STATS', 'PLAYER': '', 'VALUE': '' })
        csv_writer.writerow({ 'TEAM': '', 'PLAYER': 'Average', 'VALUE': statistics.mean(sums) })
        csv_writer.writerow({ 'TEAM': '', 'PLAYER': 'Median', 'VALUE': statistics.median(sums) })
        csv_writer.writerow({ 'TEAM': '', 'PLAYER': 'Std Dev', 'VALUE': statistics.pstdev(sums) })

    print('---------------------- Team Stats ----------------------')
    print(f'Average:\t{statistics.mean(sums)}')
    print(f'Median :\t{statistics.median(sums)}')
    print(f'Std Dev:\t{statistics.pstdev(sums)}')



def UsageError():
    print("USAGE: `python3 groupTeams.py <players> <teamSize> [randomTiered] [botValue]`")
    print("PARAM players: string representing the path to the player value CSV file (with header row)")
    print("PARAM teamSize: integer representing the number of players per team")
    print("PARAM (optional) randomTiered: true/false (default false) -- true to use random tier-based teams instead of best-first grouping")
    print("PARAM (optional) botValue: decimal number representing the value of bots if needed to pad teams. Defaults to 3")
    exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        UsageError()

    players = str(sys.argv[1])
    teamSize = int(sys.argv[2])

    randomTiered = False

    if len(sys.argv) > 3:
        randomTiered = sys.argv[3].lower() == 'true'

    if len(sys.argv) == 5:
        BOT_VALUE = float(sys.argv[4])
    

    CreateTeams(players, teamSize, randomTiered)

    print("Done.")
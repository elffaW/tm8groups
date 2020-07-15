# tm8groups

Takes a CSV of players (player,value) with header row, and groups those players into even teams using a best-first bin-packing heuristic.

### Output

Prints the teams to console, and writes to `teams.csv` file.

## Requirements

- **Python 3.8** (can use lower Python 3.x if you don't want to see all of the printed information from the statistics package)

### Parameters

USAGE: `python3 groupTeams.py <players> <teamSize> [botValue]`

- **players** (file path) the CSV file of players
  - should be formatted like (player,value)
  - should include header row
- **teamSize** (integer) how many players per team
- **botValue** *optional* (float) the assumed value of bots (used as filler if needed to make even teams)
  - defaults to **3**

import random
import sqlite3
import statistics
import json
from flask import Flask
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
conn = sqlite3.connect("lolmanager.db")
curr = conn.cursor()
team = "HLE"
role = "Top"
#curr.execute("DELETE FROM Players WHERE NAME IS NULL", ())
# curr.execute("INSERT INTO Players(NAME) VALUES (?)", ("Knight",))
# conn.commit()
teams = ["HLE", "GenG" , "T1", "DK", "KT", "FOX", "KDF", "NS", "DRX", "BRO"]
teamMap = {}
start_team_record = {}
for team in teams:
    teamMap[team] = curr.execute("SELECT * FROM Players WHERE TEAM = (?)", (team,)).fetchall()
    start_team_record[team]= [0,0]
# curr.execute("UPDATE Players SET OVERALL = (?) WHERE TRADING IS NULL", (60,))
# conn.commit()
def setRecord():
   for team in teams:
       start_team_record[team]= [0,0]
def overallCalc():
    for team in teams:
        for player in teamMap[team]:
            stats = []
            name = player[0]
            for stat in player:
                if type(stat) is int:
                    stats.append(stat)
            if len(stats)>0:
                overall = statistics.mean(stats)
                curr.execute("UPDATE Players SET OVERALL = (?) WHERE NAME = (?)", (overall, name, ))
                conn.commit()
overallCalc()

def Game(team1, team2):
    #take overalls of team members of each team and add to a list
    team1Ratings = []
    team2Ratings = []
    for player in teamMap[team1]:
        team1Ratings.append(player[1])
    for player in teamMap[team2]:
        team2Ratings.append(player[1])
    
    #find team overall by averaging player overalls
    team1Overall = statistics.mean(team1Ratings)
    team2Overall = statistics.mean(team2Ratings)
    #set variables to specific values for next part depending on which team has greater overall
    if team1Overall>team2Overall:
        greater = team1Overall
        lesser = team2Overall
        team = team1
        opp_team = team2
    else:
        greater = team2Overall
        lesser = team2Overall
        team = team2
        opp_team = team1
    
    #randomly generate a number that is used for rng, the greater the difference the less impact the rng will have
    rng = random.randint(0,99)
    diff = greater - lesser

    #simple algorithm that takes team overall difference and represents probability of match result based on the difference and prints a simulation of one game result
    match diff:
        case num if num>=30:
            if rng<=89:
                return team
            else:
                return opp_team
        case num if 30>num>=20:
            if rng<=79:
                return team
            else:
                return opp_team
        case num if 20>num>=10:
            if rng<=69:
                return team
            else:
                return opp_team
        case num if 10>num>=5:
            if rng<=59:
                return team
            else:
                return opp_team
        case num if 5>num>=2:
            if rng<=55:
                return team
            else:
                return opp_team
        case _:
            if rng<=52:
                return team
            else:
                return opp_team

#code to simulate a BO3 for the regular spit by calling the game function until one team wins 2 games
def BO3(team1, team2):
    team1_wins, team2_wins = 0, 0
    while team1_wins < 2 and team2_wins < 2:
        result = Game(team1, team2)
        if result == team1:
            team1_wins+=1
        else:
            team2_wins+=1
    if team1_wins == 2:
        return team1, team2
    else:
        return team2, team1
#same as bo3 but now for bo5
def BO5(team1, team2):
    team1_wins, team2_wins = 0, 0
    while team1_wins < 3 and team2_wins < 3:
        result = Game(team1, team2)
        if result == team1:
            team1_wins+=1
        else:
            team2_wins+=1
    if team1_wins == 3:
        return team1 , team2, str(team1_wins) + ":" + str(team2_wins)
    else:
        return team2 , team1, str(team2_wins) + ":" + str(team1_wins)
def round_robin(teams, start_team_record):
        team_record = start_team_record.copy()
        n = len(teams)
        matchs = []
        fixtures = []
        return_matchs = []
        for fixture in range(1, n):
            for i in range(n//2):
                matchs.append((teams[i], teams[n - 1 - i]))
                return_matchs.append((teams[n - 1 - i], teams[i]))
            teams.insert(1, teams.pop())
            fixtures.insert(len(fixtures)//2, matchs)
            fixtures.append(return_matchs)
            matchs = []
            return_matchs = []

        for fixture in fixtures:
            for game in fixture:
                result = BO3(game[0], game[1])
                team_record[result[0]][0] += 1
                team_record[result[1]][1] += 1
        return team_record
def regular_split_end(year):
        team_record = round_robin(teams, start_team_record)
        playoff_teams=[]
        standings = []
        sorted_dict = dict(sorted(team_record.items(), key=lambda item: item[1][0], reverse=True))
        seed = 1
        for team, record in sorted_dict.items():
            standings.append(f"{seed} {team} {record[0]}-{record[1]}")
            if seed<7:
                playoff_teams.append(team)
            seed+=1
        max = 0
        for player in teamMap[playoff_teams[0]]:
            if player[1]>max:
                curr_MVP = player[0]
                max = player[1]
        print(year, "MVP is", curr_MVP, "\n")
        return playoff_teams, curr_MVP, standings
def playoffs(playoff_teams):
        curr_teams = playoff_teams.copy()
        print("First Round")
        print(curr_teams[2], curr_teams[5])
        res1 = BO5(curr_teams[2], curr_teams[5])
        print(res1[0], "wins", res1[2])
        print(curr_teams[3], curr_teams[4])
        res2 = BO5(curr_teams[3], curr_teams[4])
        print(res2[0], "wins", res2[2])
        curr_teams.remove(res1[1])
        curr_teams.remove(res2[1])
        print()

        print("Second Round")
        print(curr_teams[0], curr_teams[3])
        res1 = BO5(curr_teams[0], curr_teams[3])
        print(res1[0], "wins", res1[2])
        print(curr_teams[1], curr_teams[2])
        res2 = BO5(curr_teams[1], curr_teams[2])
        print(res2[0], "wins", res2[2])
        curr_teams.remove(res1[1])
        curr_teams.remove(res2[1])
        print()

        print("Finals")
        print(curr_teams[0], "vs", curr_teams[1])
        res1 = BO5(curr_teams[0], curr_teams[1])
        print(res1[0], "wins", res1[2])
        curr_teams.remove(res1[1])
        return curr_teams
def split(year):
    values = {}
    print(year, "split")
#code to schedule a round robin that makes a round robin schedule for the league and then calls bo3 on every match, it also updates the team_record dictionary created earlier with wins and losses based on results
    #sorts the teams records by wins in order to find standings
    playoff_teams, MVP, standings = regular_split_end(year)
    values["playoff_teams"] = playoff_teams
    values["MVP"] = MVP
    values["standings"] = standings
    setRecord()
    #simple playoff format, will change eventually to account for various factors but in this simulation the lowest seed always plays the highest seed
    champion = playoffs(playoff_teams)
    values["champion"] = champion[0]
    return values
@app.route('/split/<int:year>', methods=('GET', 'POST'))
def split_data(year):
    values = split(year)
    return json.dumps(values)
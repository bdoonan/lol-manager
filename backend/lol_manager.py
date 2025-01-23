import random
import sqlite3
import statistics
import json
from flask import Flask, jsonify
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
conn = sqlite3.connect("lolmanager.db")
curr = conn.cursor()
curr.execute("DELETE FROM History")
conn.commit()
team = "HLE"
role = "Top"
teams = ["HLE", "GenG" , "T1", "DK", "KT", "FOX", "KDF", "NS", "DRX", "BRO"]
teamMap = {}
start_team_record = {}
selected_stats = ["Name", "Overall", "Trading", "Teamfighting", "Vision", "Roaming", "Farming", "Sidelaning", "Motivation"]
stats = ', '.join(selected_stats)
# curr.execute("UPDATE PLAYERS SET Trading = ?, Teamfighting = ?, Vision = ?, Roaming = ?, Farming = ?, Sidelaning = ? WHERE TEAM = ?", (64,64,64,64,64,64, "DK"))
# conn.commit()
for team in teams:
    teamMap[team] = curr.execute(f"SELECT {stats} FROM Players WHERE TEAM = (?)", (team,)).fetchall()
    start_team_record[team]= [0,0]
def setRecord():
   for team in teams:
       start_team_record[team]= [0,0]
# for team, players in teamMap.items():
#     curr.execute("UPDATE TEAMS SET Top = ?, Jg = ?, Mid = ?, Adc = ?, Sup = ? WHERE NAME = ?", (players[0][0], players[1][0], players[2][0], players[3][0], players[4][0], team))
def overallCalc():
    for team in teams:
        team_overall_list = []
        for player in teamMap[team]:
            stats = []
            name = player[0]
            for stat in range(2,len(player)):
                if type(player[stat]) is int:
                    stats.append(player[stat])
            if len(stats)>0:
                overall = round(statistics.mean(stats))
                team_overall_list.append(overall)
                curr.execute("UPDATE Players SET OVERALL = (?) WHERE NAME = (?)", (overall, name, ))
                conn.commit()
        if len(team_overall_list)>1:
            team_overall = statistics.mean(team_overall_list)
            curr.execute("UPDATE Teams SET OVERALL = (?) WHERE NAME = (?)", (team_overall, team, ))
            conn.commit()
overallCalc()

def Game(team1, team2):
    #select team overall from the database
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    team1Overall = curr.execute("SELECT OVERALL FROM Teams WHERE NAME = (?)", (team1,)).fetchone()[0]
    team2Overall = curr.execute("SELECT OVERALL FROM Teams WHERE NAME = (?)", (team2,)).fetchone()[0]
    conn.close()
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
        return playoff_teams, curr_MVP, standings
def playoffs(playoff_teams):
        curr_teams = playoff_teams.copy()
        res1 = BO5(curr_teams[2], curr_teams[5])
        res2 = BO5(curr_teams[3], curr_teams[4])
        #remove losers
        curr_teams.remove(res1[1])
        curr_teams.remove(res2[1])
        #remove losers
        res1 = BO5(curr_teams[0], curr_teams[3])
        res2 = BO5(curr_teams[1], curr_teams[2])
        
        curr_teams.remove(res1[1])
        curr_teams.remove(res2[1])
        #finals
        res1 = BO5(curr_teams[0], curr_teams[1])
        curr_teams.remove(res1[1])
        return curr_teams
def save_season_results(year, mvp, standings, champion):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    # Prepare the data for insertion
    curr.execute("""
        INSERT INTO History (year, mvp, standings, champion)
        VALUES (?, ?, ?, ?)
    """, (
        year,
        mvp,
        json.dumps(standings),  # Convert list to JSON string
        champion
    ))

    conn.commit()
    curr.close()
    conn.close()
def split(year):
    values = {}
    playoff_teams, MVP, standings = regular_split_end(year)
    values["playoff_teams"] = playoff_teams
    values["MVP"] = MVP
    values["standings"] = standings
    champion = playoffs(playoff_teams)
    save_season_results(year, MVP, standings, champion[0])
    setRecord()
    #simple playoff format, will change eventually to account for various factors but in this simulation the lowest seed always plays the highest seed
    values["champion"] = champion[0]
    return values
@app.route('/split/<int:year>', methods=('GET', 'POST'))
def split_data(year):
    values = split(year)
    return json.dumps(values)
@app.route('/season_history', methods=['GET'])
def get_season_history():
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()

    # Retrieve all seasons from the database
    curr.execute("SELECT * FROM History ORDER BY year DESC")
    seasons = curr.fetchall()

    # Convert the result into a list of dictionaries
    seasons_data = []
    for season in seasons:
        seasons_data.append({
            "year": season[0],
            "mvp": season[1],
            "champion": season[2],
            "standings": json.loads(season[3])
        })

    conn.close()
    
    return jsonify(seasons_data)
@app.route('/rosters', methods=['GET'])
def get_team_rosters():
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    # Retrieve all seasons from the database
    curr.execute("SELECT * FROM Teams")
    teams = curr.fetchall()

    # Convert the result into a list of dictionaries
    team_rosters = []
    for team in teams:
        curr.execute("SELECT * FROM Players WHERE NAME = ?", (team[1],))
        top_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players WHERE NAME = ?", (team[2],))
        jg_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players WHERE NAME = ?", (team[3],))
        mid_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players WHERE NAME = ?", (team[4],))
        adc_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players WHERE NAME = ?", (team[5],))
        sup_stats = curr.fetchall()
        team_rosters.append({
            "name": team[0],
            "top": team[1],
            "jg": team[2],
            "mid": team[3],
            "adc": team[4],
            "sup": team[5],
            "top_stats": top_stats,
            "jg_stats": jg_stats,
            "mid_stats": mid_stats,
            "adc_stats": adc_stats,
            "sup_stats": sup_stats
        })

    conn.close()
    
    return jsonify(team_rosters)
import random
import sqlite3
import statistics
import json
from flask import Flask, jsonify, request
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# conn = sqlite3.connect("lolmanager.db")
# curr = conn.cursor()
# curr.execute("DELETE FROM History")
#curr.execute("DELETE FROM Saved_Sims")
#curr.execute("DELETE FROM Players_Sims")
#conn.commit()
#create a teamMap and recordMap for the teams
teams = ["HLE", "GenG" , "T1", "DK", "KT", "FOX", "KDF", "NS", "DRX", "BRO"]
teamMap = {}
start_team_record = {}
# curr.execute("UPDATE PLAYERS SET Trading = ?, Teamfighting = ?, Vision = ?, Roaming = ?, Farming = ?, Sidelaning = ? WHERE TEAM = ?", (64,64,64,64,64,64, "DK"))
# conn.commit()
#function to create a map for all team and relevant player statistics using sql values
def makeTeams(sim_id):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    selected_stats = ["Name", "Overall", "Trading", "Teamfighting", "Vision", "Roaming", "Farming", "Sidelaning", "Motivation"]
    stats = ', '.join(selected_stats)
    for team in teams:
        teamMap[team] = curr.execute(f"SELECT {stats} FROM Players_Sims WHERE TEAM = (?) AND ID = (?)", (team,sim_id)).fetchall()
    return teamMap
#function called to start a new sim given name 
def startSim(name):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    year = 2025
    #inserts the year and name into the saved_sims table where unique autoincrement id is generated
    curr.execute("INSERT INTO Saved_Sims(Name, Year) VALUES (?,?)", (name, year))
    conn.commit()
    #retrieve this id to use when populating other tables
    curr.execute("SELECT Id FROM Saved_Sims WHERE Name = ?", (name,))
    id = curr.fetchone()[0]
    #insert all elements from the original players table into players_sims table with the generated id to identify which sim these players come from 
    curr.execute('''
    INSERT INTO Players_Sims (ID, Name, Overall, Trading, Teamfighting, Vision, Roaming, Farming, Sidelaning, Shotcalling, Creativity, Teamwork, Loyalty, Consistency, Team, Motivation, Role, Age, "Military Exemption", "Contract years", "Contract amount", Potential)
    SELECT ?, Name, Overall, Trading, Teamfighting, Vision, Roaming, Farming, Sidelaning, Shotcalling, Creativity, Teamwork, Loyalty, Consistency, Team, Motivation, Role, Age, "Military Exemption", "Contract years", "Contract amount", Potential
    FROM Players
    ''', (id,))
    #do the same thing for teams that was done for the players
    curr.execute('''
    INSERT INTO Teams_Sims (Id, Name, Top, Jg, Mid, Adc, Sup, Prestige, Overall)
    SELECT ?, Name, Top, Jg, Mid, Adc, Sup, Prestige, Overall
    FROM Teams             
    ''', (id,))
    conn.commit()
    #return the id so that we can send the id to the frontend so it knows what id to reference
    return id
def loadSim(name):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    #get the existing id where the entered name is and return it
    curr.execute("SELECT Id FROM Saved_Sims WHERE Name = ?", (name,))
    id = curr.fetchone()[0]
    return id   
def deleteSim(name):
    #delete from all tables all elements with the sim name's id
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    curr.execute("SELECT Id FROM Saved_Sims WHERE Name = ?", (name,))
    id = curr.fetchone()[0]
    curr.execute("DELETE FROM Saved_Sims WHERE ID = ?", (id,))
    curr.execute("DELETE FROM Players_Sims WHERE ID = ?", (id,))
    curr.execute("DELETE FROM Teams_Sims WHERE ID = ?", (id,))
    conn.commit()
    conn.close()
def setRecord():
   #set record back to start of season
   for team in teams:
       start_team_record[team]= [0,0]
# for team, players in teamMap.items():
#     curr.execute("UPDATE TEAMS SET Top = ?, Jg = ?, Mid = ?, Adc = ?, Sup = ? WHERE NAME = ?", (players[0][0], players[1][0], players[2][0], players[3][0], players[4][0], team))
setRecord()
#function to use to calculate overall, was initially used for original database but now will be used when players' stats change over the course of simulations
def overallCalc(sim_id):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    #make a teamMap for the players to use
    teamMap = makeTeams(sim_id)
    for team in teams:
        team_overall_list = []
        for player in teamMap[team]:
            stats = []
            name = player[0]
            #for every player add their numerical stats to the stats array
            for stat in range(2,len(player)):
                if type(player[stat]) is int:
                    stats.append(player[stat])
            #if the player has stats average them and round to the nearest whole number
            if len(stats)>0:
                overall = round(statistics.mean(stats))
                #add the player's overall to the team's overall list to be averaged later
                team_overall_list.append(overall)
                #update the player's overall in the sql table
                curr.execute("UPDATE Players_Sims SET OVERALL = (?) WHERE NAME = (?) AND ID = (?)", (overall, name, sim_id,))
                conn.commit()
        #after doing it for all the players update the team's overall
        if len(team_overall_list)>1:
            team_overall = statistics.mean(team_overall_list)
            curr.execute("UPDATE Teams_Sims SET OVERALL = (?) WHERE NAME = (?) AND ID = (?)", (team_overall, team, sim_id,))
            conn.commit()
    conn.close()
#function to get the current year so that we make sure split simulations are called for correct years. Return the year to the endpoint accessed in the frontend
@app.route('/<int:id>/year', methods=['GET'])
def get_year(id):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    #get the max year for the current simulation as that is one before current year
    curr.execute("SELECT MAX(year) FROM History WHERE ID = (?)", (id,))
    year = curr.fetchone()[0]  # Get the latest year from the query result
    conn.close()
    #if there is nothing in history then we are on a fresh sim and therefore in 2025
    if year is None:
        # If no season history exists, return 2025 as default
        return {"year": 2025}
    #else return the last year + 1 to get the current year
    return {"year": year+1}
#function to simulate a game
def Game(sim_id,team1, team2):
    
    #select team overall from the database
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    team1Overall = curr.execute("SELECT OVERALL FROM Teams_Sims WHERE NAME = (?) AND ID = (?)", (team1,sim_id,)).fetchone()[0]
    team2Overall = curr.execute("SELECT OVERALL FROM Teams_Sims WHERE NAME = (?) AND ID = (?)", (team2,sim_id,)).fetchone()[0]
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
def BO3(sim_id, team1, team2):
    team1_wins, team2_wins = 0, 0
    while team1_wins < 2 and team2_wins < 2:
        result = Game(sim_id, team1, team2)
        if result == team1:
            team1_wins+=1
        else:
            team2_wins+=1
    if team1_wins == 2:
        return team1, team2
    else:
        return team2, team1
#same as bo3 but now for bo5
def BO5(sim_id, team1, team2):
    team1_wins, team2_wins = 0, 0
    while team1_wins < 3 and team2_wins < 3:
        result = Game(sim_id, team1, team2)
        if result == team1:
            team1_wins+=1
        else:
            team2_wins+=1
    if team1_wins == 3:
        return team1 , team2, str(team1_wins) + ":" + str(team2_wins)
    else:
        return team2 , team1, str(team2_wins) + ":" + str(team1_wins)
#function to simulate a double roundrobin format
def round_robin(sim_id, teams, start_team_record):
        #copy the team_record since we are changing it
        team_record = start_team_record.copy()
        n = len(teams)
        matchs = []
        fixtures = []
        return_matchs = []
        #we use fixtures to create an array of matches with each team playing each other twice
        for fixture in range(1, n):
            for i in range(n//2):
                matchs.append((teams[i], teams[n - 1 - i]))
                return_matchs.append((teams[n - 1 - i], teams[i]))
            teams.insert(1, teams.pop())
            fixtures.insert(len(fixtures)//2, matchs)
            fixtures.append(return_matchs)
            matchs = []
            return_matchs = []
        # now that we have the matches we simulate them as BO3 and add a win to the winning team in the team_record and a loss for the losing team
        for fixture in fixtures:
            for game in fixture:
                result = BO3(sim_id, game[0], game[1])
                team_record[result[0]][0] += 1
                team_record[result[1]][1] += 1
        return team_record
#this function is used to sort the standings, playoff teams, and mpv
def regular_split_end(sim_id):
        #make a teamMap to get player stats
        teamMap = makeTeams(sim_id)
        #call round robin to simulate the season
        team_record = round_robin(sim_id, teams, start_team_record)
        playoff_teams=[]
        standings = []
        #sort the team_records from most wins to least wins
        sorted_dict = dict(sorted(team_record.items(), key=lambda item: item[1][0], reverse=True))
        seed = 1
        #populate the standings array with the team's seed, name, and record
        for team, record in sorted_dict.items():
            standings.append(f"{seed} {team} {record[0]}-{record[1]}")
            #if the team is top 6 add them to the playoffs
            if seed<7:
                playoff_teams.append(team)
            seed+=1
        max = 0
        #currently not the best algorithm but MVP is awarded to the highest overall player on the number 1 seeded team
        for player in teamMap[playoff_teams[0]]:
            if player[1]>max:
                curr_MVP = player[0]
                max = player[1]
        #return playoff teams, MVP, and standings
        return playoff_teams, curr_MVP, standings
#simulate a single elimination playoff bracket with the playoff team array and bo5 matches
#currently top seeded teams always play the lowest seeded ones, but I may try to add variance and factor in overall, head to head, and team history
def playoffs(sim_id, playoff_teams):
        curr_teams = playoff_teams.copy()
        res1 = BO5(sim_id, curr_teams[2], curr_teams[5])
        res2 = BO5(sim_id, curr_teams[3], curr_teams[4])
        #remove losers
        curr_teams.remove(res1[1])
        curr_teams.remove(res2[1])
        #remove losers
        res1 = BO5(sim_id, curr_teams[0], curr_teams[3])
        res2 = BO5(sim_id, curr_teams[1], curr_teams[2])
        
        curr_teams.remove(res1[1])
        curr_teams.remove(res2[1])
        #finals
        res1 = BO5(sim_id, curr_teams[0], curr_teams[1])
        curr_teams.remove(res1[1])
        return curr_teams
#function to insert all season stats into history table
def save_season_results(sim_id, year, mvp, standings, champion):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    # Prepare the data for insertion
    curr.execute("""
        INSERT INTO History (year, mvp, standings, champion, id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        year,
        mvp,
        json.dumps(standings),  # Convert list to JSON string
        champion,
        sim_id
    ))

    conn.commit()
    conn.close()
#function to simulate a full season
def split(sim_id, year):
    values = {}
    playoff_teams, MVP, standings = regular_split_end(sim_id)
    values["playoff_teams"] = playoff_teams
    values["MVP"] = MVP
    values["standings"] = standings
    champion = playoffs(sim_id, playoff_teams)
    save_season_results(sim_id, year, MVP, standings, champion[0])
    setRecord()
    #simple playoff format, will change eventually to account for various factors but in this simulation the lowest seed always plays the highest seed
    values["champion"] = champion[0]
    return values
#returns the split values to the api endpoint to be called and retrieved in the frontend
@app.route('/split/<int:id>/<int:year>', methods=('GET', 'POST'))
def split_data(id, year):
    #simulate the season for the current sim
    values = split(id, year)
    return json.dumps(values)
#returns history starting from the lastest year to the api endpoint to be retrieved in the frontend
@app.route('/<int:id>/season_history', methods=['GET'])
def get_season_history(id):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()

    # Retrieve all seasons from the database for the current sim
    curr.execute("SELECT * FROM History WHERE ID = (?) ORDER BY year DESC", (id,))
    seasons = curr.fetchall()

    
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
#returns the rosters for all teams in the current sim
@app.route('/<int:id>/rosters', methods=['GET'])
def get_team_rosters(id):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    # Retrieve all players for each team from the database for the current sim
    curr.execute("SELECT * FROM Teams_Sims WHERE ID = ?", (id,))
    teams = curr.fetchall()

    team_rosters = []
    #get all the stats for the players for each team from the players_sims table 
    for team in teams:
        curr.execute("SELECT * FROM Players_Sims WHERE NAME = ? AND ID = ?", (team[1],id,))
        top_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players_Sims WHERE NAME = ? AND ID = ?", (team[2],id,))
        jg_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players_Sims WHERE NAME = ? AND ID = ?", (team[3],id,))
        mid_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players_Sims WHERE NAME = ? AND ID = ?", (team[4],id,))
        adc_stats = curr.fetchall()
        curr.execute("SELECT * FROM Players_Sims WHERE NAME = ? AND ID = ?", (team[5],id,))
        sup_stats = curr.fetchall()
        #return player names and their stats to the endpoint
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
#gets the name from the input field in the frontend
@app.route('/start_sim', methods=['POST'])
def start_sim():
    data = request.get_json()
    sim_name = data.get('simulationName')
    #calls startSim for the retrieved name
    sim_id = startSim(sim_name)
    #return the generated id
    return jsonify({'simulationId': sim_id})
#gets sim name from the frontend to load
@app.route('/load_sim/<sim_name>', methods=['GET'])
def load_sim(sim_name):
    sim_id = loadSim(sim_name)
    #return the id for the inputted name
    return jsonify({'simulationId': sim_id})
#deletes the sim with the inputted name from all database tables
@app.route('/delete_sim/<sim_name>', methods=['GET'])
def delete_sim(sim_name):
    deleteSim(sim_name)
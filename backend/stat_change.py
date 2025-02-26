import sqlite3
import random
def offseason(sim_id):
    conn = sqlite3.connect("lolmanager.db")
    curr = conn.cursor()
    curr.execute("UPDATE Players_Sims SET Age = Age+1 WHERE Id = (?)", (sim_id,))
    curr.execute("UPDATE Players_Sims SET [Contract Years] = [Contract Years]-1 WHERE Id = (?)", (sim_id,))
    conn.commit()
    curr.execute("SELECT Name, Role, Team, Overall, Loyalty FROM Players_Sims WHERE [Contract Years] = 0 AND ID = (?) ORDER BY Overall DESC", (sim_id,))
    expired = curr.fetchall()
    signed_players = []
    for player in expired:
        rng = random.randint(0,99)
        player_name = player[0]
        player_role = player[1]
        team = player[2]
        overall = player[3]
        loyalty = player[4]
        # curr.execute("SELECT Prestige, Overall FROM Teams_Sims WHERE NAME = (?) AND ID = (?)", (team, sim_id,))
        # team_stats = curr.fetchone()
        if player_role:  # Ensure the role is not empty
            query = f"UPDATE Teams_Sims SET {player_role} = NULL WHERE Name = (?) AND ID = (?)"
            curr.execute(query, (team,sim_id))
            curr.execute("UPDATE Players_Sims SET TEAM = NULL WHERE NAME = (?) AND ID = (?)", (player_name, sim_id))
        match loyalty:
            case num if num>90:
                if rng > 10:
                    curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team, player_name, sim_id))
                    query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                    curr.execute(query, (player_name, team, sim_id))
                    signed_players.append(player_name)
            case num if num>80:
                if rng > 20:
                    curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team, player_name, sim_id))
                    query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                    curr.execute(query, (player_name, team, sim_id))
                    signed_players.append(player_name)
            case _:
                if rng > 50:
                    curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team, player_name, sim_id))
                    query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                    curr.execute(query, (player_name, team, sim_id))
                    signed_players.append(player_name)
    for player in expired:
        player_name = player[0]
        player_role = player[1]
        overall = player[3]
        curr.execute("SELECT Team FROM Players_Sims WHERE Name = (?) AND id = (?)", (player_name, sim_id))
        player_team = curr.fetchone()[0]
        if player_team is None:
            query = f"SELECT Name, Prestige FROM Teams_Sims WHERE {player_role} IS NULL AND ID = (?) ORDER BY OVERALL DESC"
            curr.execute(query, (sim_id,))
            possible_teams = curr.fetchall()
            for team in possible_teams:
                rng = random.randint(0,99)
                team_name = team[0]
                team_prestige = team[1]
                if team_prestige>=90:
                    if rng > 20:
                        curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team_name, player_name, sim_id))
                        query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                        curr.execute(query, (player_name, team_name, sim_id))
                        break
                elif team_prestige>=80:
                    if rng > 30:
                        curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team_name, player_name, sim_id))
                        query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                        curr.execute(query, (player_name, team_name, sim_id))
                        break
                elif team_prestige>=70:
                    if rng > 40:
                        curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team_name, player_name, sim_id))
                        query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                        curr.execute(query, (player_name, team_name, sim_id))
                        break
                else:
                    if rng > 50:
                        curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team_name, player_name, sim_id))
                        query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                        curr.execute(query, (player_name, team_name, sim_id))
                        break
    for player in expired:
        player_name = player[0]
        player_role = player[1]
        overall = player[3]
        curr.execute("SELECT Team FROM Players_Sims WHERE Name = (?) AND id = (?)", (player_name, sim_id))
        player_team = curr.fetchone()[0]
        if player_team is None:
            query = f"SELECT Name FROM Teams_Sims WHERE {player_role} IS NULL AND ID = (?) ORDER BY OVERALL DESC"
            curr.execute(query, (sim_id,))
            possible_teams = curr.fetchall()
            for team in possible_teams:
                team_name = team[0]
                
                curr.execute("UPDATE Players_Sims SET [Contract Years] = 1, TEAM = (?) WHERE NAME = (?) AND ID = (?)", (team_name, player_name, sim_id))
                query = f"UPDATE Teams_Sims SET {player_role} = (?) WHERE Name = (?) AND ID = (?)"
                curr.execute(query, (player_name, team_name, sim_id))
                break

                              
        


    conn.commit()
    
    conn.close()
    return sim_id
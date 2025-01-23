import React, { useState, useEffect } from 'react';

function App() {
  const [year, setYear] = useState(2024); // Default to 2024
  const [splitData, setSplitData] = useState(null);
  const [seasonHistory, setSeasonHistory] = useState([]);
  const [teams, setTeams] = useState([]); // Holds the fetched team rosters
  const [currentTeamIndex, setCurrentTeamIndex] = useState(0); // Tracks which team's roster to display
  const [showRoster, setShowRoster] = useState(false); // Toggles between roster view and original view
  const [showHistory, setShowHistory] = useState(false); // Toggles between season history view and original view

  // Fetch team rosters from the backend
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await fetch('/rosters');
        if (!response.ok) {
          throw new Error('Failed to fetch team rosters');
        }
        const data = await response.json();
        setTeams(data); // Set the fetched team data to state
      } catch (error) {
        console.error('Error fetching team rosters:', error);
      }
    };

    fetchTeams(); // Fetch team rosters when the component mounts
  }, []);

  // Function to simulate a new season (new split)
  const handleSplitClick = async () => {
    try {
      // Send a GET request to your Flask server to trigger the new split for the next year
      const response = await fetch(`/split/${year}`);
      const data = await response.json();

      // Set the result data to display
      setSplitData(data);

      // Increment the year for the next split
      setYear(prevYear => prevYear + 1); // Move to the next year
    } catch (error) {
      console.error('Error fetching split data:', error);
    }
  };

  // Function to fetch the season history from the backend
  const fetchSeasonHistory = async () => {
    try {
      const response = await fetch('/season_history');
      if (!response.ok) {
        throw new Error('Failed to fetch season history');
      }
      const data = await response.json();
      setSeasonHistory(data);
      setShowHistory(true); // Show season history when fetched
    } catch (error) {
      console.error('Error fetching season history:', error);
    }
  };

  // Function to cycle through the teams
  const nextTeam = () => {
    setCurrentTeamIndex((prevIndex) => (prevIndex + 1) % teams.length);
  };

  const prevTeam = () => {
    setCurrentTeamIndex((prevIndex) => (prevIndex - 1 + teams.length) % teams.length);
  };

  return (
    <div>
      <h1>League Manager</h1>

      {/* Button to simulate a new split */}
      <div>
        <h2>Start New Split</h2>
        <button onClick={handleSplitClick}>Start Split for {year}</button>

        {splitData && (
          <div>
            <h3>Results for {year-1} Split:</h3>
            <p><strong>MVP:</strong> {splitData.MVP}</p>
            <p><strong>Playoff Teams:</strong> {splitData.playoff_teams.join(', ')}</p>
            <p><strong>Champion:</strong> {splitData.champion}</p>
            <h4>Standings:</h4>
            <ul>
              {Array.isArray(splitData.standings) && splitData.standings.map((standing, index) => (
                <li key={index}>{standing}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <hr />

      {/* Button to view season history */}
      <div>
        <h2>Season History</h2>
        {!showHistory ? (
          <button onClick={fetchSeasonHistory}>View Season History</button>
        ) : (
          <button onClick={() => setShowHistory(false)}>Close Season History</button>
        )}

        {showHistory && (
          <div>
            <h3>Season History</h3>
            <ul>
              {seasonHistory.map((season, index) => (
                <li key={index}>
                  <strong>Year:</strong> {season.year}<br />
                  <strong>MVP:</strong> {season.mvp}<br />
                  <strong>Champion:</strong> {season.champion}<br />
                  <strong>Standings:</strong> {season.standings.join(', ')}
                  <hr />
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <hr />

      {/* Button to toggle roster view */}
      <div>
        <button onClick={() => setShowRoster(!showRoster)}>
          {showRoster ? 'Close Rosters' : 'Show Rosters'}
        </button>

        {showRoster && teams.length > 0 && (
          <div>
            <h2>{teams[currentTeamIndex].name} Roster</h2>
            <table>
              <thead>
                <tr>
                  <th>Position</th>
                  <th>Player</th>
                  <th>Overall</th>
                  <th>Trading</th>
                  <th>Teamfighting</th>
                  <th>Vision</th>
                  <th>Roaming</th>
                  <th>Farming</th>
                  <th>Sidelaning</th>
                  <th>Shotcalling</th>
                  <th>Loyalty</th>
                  <th>Consistency</th>
                  <th>Motivation</th>
                  <th>Age</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Top</td>
                  <td>{teams[currentTeamIndex].top}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][1]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][2]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][3]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][4]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][5]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][6]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][7]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][8]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][11]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][12]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][14]}</td>
                  <td>{teams[currentTeamIndex].top_stats[0][16]}</td>
                </tr>
                <tr>
                  <td>Jungle</td>
                  <td>{teams[currentTeamIndex].jg}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][1]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][2]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][3]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][4]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][5]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][6]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][7]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][8]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][11]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][12]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][14]}</td>
                  <td>{teams[currentTeamIndex].jg_stats[0][16]}</td>

                </tr>
                <tr>
                  <td>Mid</td>
                  <td>{teams[currentTeamIndex].mid}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][1]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][2]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][3]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][4]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][5]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][6]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][7]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][8]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][11]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][12]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][14]}</td>
                  <td>{teams[currentTeamIndex].mid_stats[0][16]}</td>
                </tr>
                <tr>
                  <td>ADC</td>
                  <td>{teams[currentTeamIndex].adc}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][1]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][2]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][3]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][4]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][5]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][6]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][7]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][8]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][11]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][12]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][14]}</td>
                  <td>{teams[currentTeamIndex].adc_stats[0][16]}</td>
                </tr>
                <tr>
                  <td>Support</td>
                  <td>{teams[currentTeamIndex].sup}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][1]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][2]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][3]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][4]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][5]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][6]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][7]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][8]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][11]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][12]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][14]}</td>
                  <td>{teams[currentTeamIndex].sup_stats[0][16]}</td>

                </tr>
              </tbody>
            </table>

            {/* Arrow buttons to cycle through teams */}
            <div>
              <button onClick={prevTeam}>← Previous Team</button>
              <button onClick={nextTeam}>Next Team →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

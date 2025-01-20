import React, { useState } from 'react';

function App() {
  const [year, setYear] = useState(2024); // Default to 2024
  const [splitData, setSplitData] = useState(null);
  const [seasonHistory, setSeasonHistory] = useState([]);

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
    } catch (error) {
      console.error('Error fetching season history:', error);
    }
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
        <h2>View Season History</h2>
        <button onClick={fetchSeasonHistory}>View Season History</button>

        {seasonHistory.length > 0 && (
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
    </div>
  );
}

export default App;

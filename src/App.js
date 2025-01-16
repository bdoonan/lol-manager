import React, { useState } from 'react';

function NewSplitButton() {
  const [year, setYear] = useState(2024); // Default to 2024
  const [splitData, setSplitData] = useState(null);

  const handleSplitClick = async () => {
    try {
      // Send a GET request to your Flask server to trigger the new split for the next year
      const response = await fetch(`/split/${year}`);
      const data = await response.json();

      // Set the result data to display
      setSplitData(data);

      // Increment the year for the next split
      setYear(year + 1); // Move to the next year
    } catch (error) {
      console.error('Error fetching split data:', error);
    }
  };

  return (
    <div>
      <h1>Start New Split</h1>
      <button onClick={handleSplitClick}>Start Split for {year}</button>
      
      {splitData && (
        <div>
          <h2>Results for {year} Split:</h2>
          <p>MVP: {splitData.MVP}</p>
          <p>Playoff Teams: {splitData.playoff_teams.join(', ')}</p>
          <p>Champion: {splitData.champion}</p>
          <h3>Standings:</h3>
          <ul>
            {splitData.standings.map((standing, index) => (
              <li key={index}>{standing}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default NewSplitButton;

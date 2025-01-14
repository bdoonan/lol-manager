import "./App.css";
import React, { useState, useEffect } from "react";

function App() {
  const [MVP, setMVP] = useState(0);
  const [playoffs, setPlay] = useState([]);
  const[champion, setChamp] = useState(0);
  useEffect(() =>{
    fetch("/data").then(response =>
      response.json().then(data=>{
        setMVP(data.MVP);
        setPlay(JSON.stringify(data.playoff_teams));
        setChamp(data.champion)
      })
    );
  }, []);

  return(
  <div className="App">
    <h1>The MVP is {MVP}</h1>
    <h1>The Playoff Teams are {playoffs}</h1>
    <h1>The Champion is {champion}</h1>
  </div>
  ) ;
}

export default App;
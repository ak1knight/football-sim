import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header" style={{
        backgroundColor: '#282c34',
        padding: '20px',
        color: 'white',
        textAlign: 'center',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 'calc(10px + 2vmin)'
      }}>
        <h1>🏈 Football Simulation Engine</h1>
        <p>Electron + React + TypeScript</p>
        <p style={{ fontSize: '16px', marginTop: '20px' }}>
          If you can see this, the basic setup is working!
        </p>
      </header>
    </div>
  );
}

export default App;
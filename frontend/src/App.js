import React, { useState } from 'react';
import './App.css';
import Home from './Pages/Home';
import About from './Pages/About';
import NewGame from './Pages/NewGame';
import LoadGame from './Pages/LoadGame';

function App() {
  const [currentPage, setCurrentPage] = useState('Home');

  return (
    <div className="App">
      <div
        className='container flex-column'
        style={{
          height: '100%',
          width: '100%',
          minWidth: '100%',
          minHeight: '100%',
          paddingTop: '8%',
          paddingBottom: '7%',
          overflow: 'auto',
        }}
      >
        {currentPage === 'Home' && (
          <Home onSetCurrentPage={(page) => setCurrentPage(page)} />
        )}
        {currentPage === 'NewGame' && (
          <NewGame onSetCurrentPage={(page) => setCurrentPage(page)} />
        )}
        {currentPage === 'LoadGame' && (
          <LoadGame onSetCurrentPage={(page) => setCurrentPage(page)} />
        )}
        {currentPage === 'About' && (
          <About onSetCurrentPage={(page) => setCurrentPage(page)} />
        )}
      </div>
    </div>
  );
}

export default App;

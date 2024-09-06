import './App.css';

import React, { useState } from 'react';

import Home from './Pages/Home';
import About from './Pages/About';
import NewGame from './Pages/NewGame';
import LoadGame from './Pages/LoadGame';

function App() {

  const [currentPage, setCurrentPage] = useState('Home');


  return (
    <div className="App">

      <div className='container' 
        style={{ display: 'flex', flexDirection: 'column',
                justifyContent: 'center', alignItems: 'center',
                height: '100vh', textAlign: 'center', 
                }}>

        {currentPage === 'Home' && 
        <Home
        onSetCurrentPage={(page) => setCurrentPage(page)}
        />}
        {currentPage === 'NewGame' &&
          <NewGame />}
        {currentPage === 'LoadGame' &&
          <LoadGame />}
        {currentPage === 'About' &&
          <About />}
    
      </div>
      
    </div>

      
     
);
}

export default App;


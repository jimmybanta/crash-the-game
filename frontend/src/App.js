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

      <div className='container flex-column' 
        style={{ 
          height: '100%',
          width: '100%',
          minWidth: '100%',
          minHeight: '100%',
          paddingTop: '7%', paddingBottom: '5%',
          overflow: 'auto',
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


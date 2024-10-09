import React from 'react';

const Home = ({ onSetCurrentPage }) => {
  // The home page 

  return (
    <div className='container flex-column' style={{ width: '100%', height: '100%' }}>
      <div className='container flex-column' style={{ width: '100%', height: '33%' }}>
        <h1 className='text header'>CRASH</h1>
      </div>

      <div className='container flex-column' style={{ width: '100%', height: '66%', gap: '5%' }}>
        <div className='button home-button text button-text' onClick={() => onSetCurrentPage('NewGame')}>
          New Game
        </div>
        <div className='button home-button text button-text' onClick={() => onSetCurrentPage('LoadGame')}>
          Load Game
        </div>
        <div className='button home-button text button-text' onClick={() => onSetCurrentPage('About')}>
          About
        </div>
      </div>
    </div>
  );
};

export default Home;

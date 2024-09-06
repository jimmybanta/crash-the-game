import { React, useState } from 'react';




const Home = ({onSetCurrentPage}) => {

    return (
    <div style={{width: '100%', height: '100%'}}>

      <div className='container'
      style={{ width: '100%', height: '33%'}}>
        <h1 className='text header'>CRASH</h1>
      </div>
      <div className='container flex-column'
      style={{ justifyContent: 'center', alignItems: 'center',
        width: '100%', height: '66%',
        gap: '5%'}}>

      
          <div
          className='home-button text'
          onClick={() => onSetCurrentPage('NewGame')}>
            New Game
          </div>
          <div
          className='home-button text'
          onClick={() => onSetCurrentPage('LoadGame')}>
            Load Game
          </div>
          <div
          className='home-button text'
          onClick={() => onSetCurrentPage('About')}>
            About
          </div>

      </div>

    </div>
    )
    }



export default Home;
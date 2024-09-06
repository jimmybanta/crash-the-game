
import { React, useEffect, useState } from 'react';
import axios from 'axios';

import { BASE_URL } from '../interceptors';

import Setup from '../Components/Setup';
import Loading from '../Components/Loading';
import Game from './Game'

axios.defaults.baseURL = BASE_URL;




const NewGame = () => {

    const [saveKey, setSaveKey] = useState('');
    const [gameId, setGameId] = useState(null);

    const [theme, setTheme] = useState('');
    const [timeframe, setTimeframe] = useState('');
    const [details, setDetails] = useState('');

    const [setupComplete, setSetupComplete] = useState(false);


    useEffect(() => {
        // we need to make an api call to the backend to get a new game key

        axios.post('/games/initialize_game_key/')
        .then(response => {
            console.log('response:', response.data);
            setSaveKey(response.data.save_key);
            setGameId(response.data.game_id);
        })
        .catch(error => {
            console.log('Error:', error);
        });
        

    }, []);
    


    const handleSetup = (theme, timeframe, details) => {
        setTheme(theme);
        setTimeframe(timeframe);
        setDetails(details);
        setSetupComplete(true);
    };

    return (
    <div className='container flex-column'
        style={{ justifyContent: 'center', alignItems: 'center',
                height: '90%', width: '80%',
        }}>

        
            {/* if we haven't setup yet, then render setup
            otherwise, render the main game */}
            { !setupComplete && <Setup onSubmit={(theme, timeframe, details) => 
                                                handleSetup(theme, timeframe, details)} />}

            {/* if we have set up, but don't have the game key yet
            then render loading */}
            { setupComplete && !saveKey && <Loading />}

            {/* if we have the game key, then render the game */}
            { setupComplete && saveKey && 
            <Game 
                theme={theme}
                timeframe={timeframe}
                details={details}
                saveKey={saveKey}
                gameId={gameId}
            />}
         
    </div>
    )

};

export default NewGame;
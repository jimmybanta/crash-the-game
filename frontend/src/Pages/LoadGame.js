import { React, useEffect, useState } from 'react';
import axios from 'axios';

import { BASE_URL } from '../interceptors';

import { generateStream } from '../streaming';

import Game from './Game';


axios.defaults.baseURL = BASE_URL;



const LoadGame = () => {
    // component that prompts the user for their save key
    // when they do that, 

    const [saveKey, setSaveKey] = useState('');

    const [gameId, setGameId] = useState(null);
    const [theme, setTheme] = useState('');
    const [timeframe, setTimeframe] = useState('');
    const [details, setDetails] = useState('');

    const [title, setTitle] = useState('');

    const [keyInput, setKeyInput] = useState(false);

    const [devMode, setDevMode] = useState('true');


    const handleKeyCheck = async () => {

        try {

            // first, get the game info
            const gameInfoResp = await axios({
                method: 'post',
                url: '/games/load_game_info/',
                data: {
                    save_key: saveKey,
                }
            });

            if (gameInfoResp.data.error) {
                alert('Invalid save key. Please try again');
                return;
            }

            setGameId(gameInfoResp.data.id);
            setTitle(gameInfoResp.data.title);
            setTheme(gameInfoResp.data.theme);
            setTimeframe(gameInfoResp.data.timeframe);
            setDetails(gameInfoResp.data.details);

            setKeyInput(true);

        }
        catch (error) {
            console.log('Error:', error);
        }




    };

    const renderSaveKeyInput = () => {

        return (
            <div className='container flex-column'
                style={{
                    paddingTop: '20px',
                    paddingBottom: '20px',
                    width: '100%',
                    height: '100%',
                }}>

                <div className='text setup-input-header'>
                    Enter your save key:
                </div>

                <input
                    className='setup-input'
                    type='text'
                    value={saveKey}
                    onChange={(e) => setSaveKey(e.target.value)}
                    style={{
                        width: '60%',
                        textAlign: 'center',
                    }}/>

                <button
                    className='button home-button text'
                    style={{ marginTop: '3%'}}
                    onClick={() => handleKeyCheck()}>
                    Load Game
                </button>
            </div>
        )


    };


    return (
        <div className='container flex-column'
            style={{ 
                    height: '100%', 
                    width: '100%',
                    minWidth: '100%',
                    minHeight: '100%',
        }}>

            {!keyInput && renderSaveKeyInput()}

            {keyInput && 
            <Game 
            gameContext={'loadGame'}
            gameId={gameId}
            title={title}
            theme={theme}
            timeframe={timeframe}
            details={details}
            saveKey={saveKey}
            devMode={devMode}
            />}


        </div>




    )
    


};


export default LoadGame;
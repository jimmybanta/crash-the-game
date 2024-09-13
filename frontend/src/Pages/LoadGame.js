import { React, useState } from 'react';
import axios from 'axios';

import Game from './Game';
import { apiCall } from '../api';
import { BASE_URL } from '../BaseURL';

axios.defaults.baseURL = BASE_URL;

const LoadGame = ({ onSetCurrentPage }) => {
    // component that prompts the user for their save key
    // when they do that, it makes an api call to get the game info
    // then it renders the game component with that info

    // the game save key
    const [saveKey, setSaveKey] = useState('');

    // game info
    const [gameId, setGameId] = useState(null);
    const [theme, setTheme] = useState('');
    const [timeframe, setTimeframe] = useState('');
    const [details, setDetails] = useState('');
    const [title, setTitle] = useState('');
    const [gameTurn, setGameTurn] = useState(null);

    // whether or not the user has input a key
    const [keyInput, setKeyInput] = useState(false);

    // for development purposes
    const devMode = 'false';

    // from the save key, gets game info
    const getGameInfo = async () => {
        // first, get the game info
        const [success, resp] = await apiCall({
            method: 'post',
            url: '/games/load_game_info/',
            data: {
                save_key: saveKey,
            },
        });

        if (!success) {
            alert(resp);
            return;
        }

        // set it
        setGameId(resp.id);
        setTitle(resp.title);
        setTheme(resp.theme);
        setTimeframe(resp.timeframe);
        setDetails(resp.details);
        setGameTurn(resp.turns);

        // now, we can render the game
        setKeyInput(true);
    };

    // render the save key input
    const renderSaveKeyInput = () => {
        return (
            <div
                className='container flex-column'
                style={{
                    paddingTop: '20px',
                    paddingBottom: '20px',
                    width: '100%',
                    height: '100%',
                }}
            >
                <div className='text setup-input-header'>Enter your save key:</div>

                <input
                    className='setup-input'
                    type='text'
                    value={saveKey}
                    onChange={(e) => setSaveKey(e.target.value)}
                    style={{
                        width: '60%',
                        textAlign: 'center',
                    }}
                />

                <div
                    className='button home-button text'
                    style={{ marginTop: '3%' }}
                    onClick={() => getGameInfo()}
                >
                    Load Game
                </div>
                <div
                    className='button back-button text'
                    style={{ marginTop: '7%' }}
                    onClick={() => onSetCurrentPage('Home')}
                >
                    Back
                </div>
            </div>
        );
    };

    return (
        <div
            className='container flex-column'
            style={{
                height: '100%',
                width: '100%',
                minWidth: '100%',
                minHeight: '100%',
            }}
        >
            {/* if they haven't put in their key yet, then prompt them for it */}
            {!keyInput && renderSaveKeyInput()}

            {/* if they have put in their key, and we have the game info, then render the game */}
            {keyInput && (
                <Game
                    gameContext={'loadGame'}
                    gameId={gameId}
                    title={title}
                    theme={theme}
                    timeframe={timeframe}
                    details={details}
                    saveKey={saveKey}
                    gameTurn={gameTurn}
                />
            )}
        </div>
    );
};

export default LoadGame;
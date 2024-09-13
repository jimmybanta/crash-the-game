import React, { useEffect, useState } from 'react';

import Setup from './Setup';
import Game from './Game';

import Loading from '../Components/Loading';

import { apiCall } from '../api';

const NewGame = ({ onSetCurrentPage }) => {
    // This component will be used to create a new game.
    // First, it makes an API call to create a new game and return the save key.
    // It prompts the user for a theme, timeframe, and details.
    // Then it renders the Game component with that info.

    // Game key & id
    const [saveKey, setSaveKey] = useState('');
    const [gameId, setGameId] = useState(null);

    // Game info
    const [theme, setTheme] = useState('');
    const [timeframe, setTimeframe] = useState('');
    const [details, setDetails] = useState('');
    // start the game at turn 0
    // this will be automatically incremented on the first turn
    const gameTurn = 0;

    // Whether or not the setup is complete
    const [setupComplete, setSetupComplete] = useState(false);

    // For development purposes
    const [devMode, setDevMode] = useState('false');

    useEffect(() => {
        // We need to make an API call to the backend to get a new game key

        const initializeSaveKey = async () => {
            // Make an API call to create the game and return the save key
            const [success, resp] = await apiCall({
                method: 'post',
                url: '/games/initialize_save_key/',
                data: { dev: devMode }
            });

            // If it was not successful, send them back to the home page to try again
            if (!success) {
                alert(resp);
                window.location.reload();
                return;
            }

            // Set the save key and game id
            setSaveKey(resp.save_key);
            setGameId(resp.game_id);
        };

        initializeSaveKey();
    }, []);

    const handleSetup = (theme, timeframe, details) => {
        setTheme(theme);
        setTimeframe(timeframe);
        setDetails(details);
        setSetupComplete(true);
    };

    return (
        <div
            className='container flex-column'
            style={{
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                width: '100%',
                minWidth: '100%'
            }}
        >
            {/* If we haven't setup yet, then render Setup */}
            {!setupComplete && (
                <Setup
                    onSetCurrentPage={(page) => onSetCurrentPage(page)}
                    onSubmit={(theme, timeframe, details) =>
                        handleSetup(theme, timeframe, details)
                    }
                />
            )}

            {/* If we have set up, but don't have the game key yet, then render Loading */}
            {setupComplete && !saveKey && <Loading size={'large'} />}

            {/* If we have the game key, then render the Game */}
            {setupComplete && saveKey && (
                <Game
                    gameContext={'newGame'}
                    theme={theme}
                    timeframe={timeframe}
                    details={details}
                    gameTurn={gameTurn}
                    saveKey={saveKey}
                    gameId={gameId}
                    devMode={devMode}
                />
            )}
        </div>
    );
};

export default NewGame;

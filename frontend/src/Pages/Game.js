import React, { useEffect, useState } from 'react';

import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';
import CharactersModal from '../Components/CharactersModal';
import Header from '../Components/Header';
import Footer from '../Components/Footer';
import Loading from '../Components/Loading';

import { apiCall, apiStream } from '../api';

const Game = (props) => {
    // our main game component
    // this gets rendered from one of two places
    // 1. NewGame - a new game is being initialized
    // 2. LoadGame - an old game is being loaded

    // five possible values for gameContext:
    // 1. newGame - a new game is being initialized
    // 2. gameIntro - a new game is being introduced to the player
    // 3. loadGame - an old game is being loaded
    // 4. gameLoaded - a game has been loaded, and we want to welcome the player back
    // 5. gamePlay - the game is being played
    const [gameContext, setGameContext] = useState(props.gameContext);

    // game details
    const [gameId, setGameId] = useState(props.gameId);
    const [saveKey, setSaveKey] = useState(props.saveKey);
    const [theme, setTheme] = useState(props.theme);
    const [timeframe, setTimeframe] = useState(props.timeframe);
    const [details, setDetails] = useState(props.details);

    // game content
    const [title, setTitle] = useState(props.title ? props.title : '');
    const [characters, setCharacters] = useState([]);
    const [skills, setSkills] = useState([]);

    // game state
    const [history, setHistory] = useState([]);
    const [currentStream, setCurrentStream] = useState('');
    const [gameTurn, setGameTurn] = useState(props.gameTurn);

    // modals
    const [saveKeyModalOpen, setSaveKeyModalOpen] = useState(false);
    const [charactersModalOpen, setCharactersModalOpen] = useState(false);

    // loading dots
    const [loading, setLoading] = useState(false);

    // input text on error - used when there's an error
    // streaming a response, to reset the input text
    const [inputTextOnError, setInputTextOnError] = useState('');

    // for development purposes
    const [devMode, setDevMode] = useState(props.devMode);

    //// useEffects
    // auto-scroll
    // run when currentStream or loading changes
    useEffect(() => {
        // if we're loading a game (or a game has loaded), scroll to the bottom of the last textbox
        if (gameContext === 'loadGame' || gameContext === 'gameLoaded') {
            window.scrollBy({ top: 500, behavior: 'instant' });
        }

        // if the user has just submitted input, scroll so the loading dots are visible
        if (loading) {
            window.scrollBy({ top: 500, behavior: 'smooth' });
        }
    }, [currentStream, loading]);

    // initialize or load the game on first render
    useEffect(() => {
        // populates the characters and the skills
        const populateInfo = async () => {
            // first, populate the characters
            const [charactersSuccess, charactersResp] = await apiCall({
                method: 'get',
                url: '/games/api/characters/',
                params: {
                    game_id: gameId,
                },
            });

            if (charactersSuccess) {
                setCharacters(charactersResp);
            }
            // if it didn't work, then characters won't be set
            // in the modal, it will display an error message

            // then, populate the skills
            const [skillsSuccess, skillsResp] = await apiCall({
                method: 'get',
                url: '/games/api/skills/',
                params: {
                    game_id: gameId,
                },
            });

            if (skillsSuccess) {
                setSkills(skillsResp);
            }
        };

        // initializes a new game
        const initializeGame = async () => {
            // first - generate the title
            const [titleSuccess, titleResp] = await apiCall({
                method: 'post',
                url: '/games/initialize_game_title/',
                data: {
                    game_id: gameId,
                    theme: theme,
                    timeframe: timeframe,
                    details: details,
                    dev: devMode,
                },
            });

            if (!titleSuccess) {
                alert('There was a problem initializing the game - please try again.');
                // redirect to home
                window.location.href = '/';
                return;
            }

            setTitle(titleResp.title);

            // then - generate the crash story
            const crashStream = await apiStream({
                method: 'POST',
                url: '/games/initialize_game_crash/',
                data: {
                    game_id: gameId,
                    dev: devMode,
                },
            });

            // stream it in
            let streamAccumulator = '';
            for await (const chunk of crashStream) {
                // check for an error chunk
                if (chunk === 'CRASH-GAME-INITIALIZATION-ERROR-ABC123') {
                    alert('There was a problem initializing the game - please try again.');
                    // redirect to home
                    window.location.href = '/';
                    return;
                }

                // add chunk to the current stream
                streamAccumulator += chunk;
                setCurrentStream(streamAccumulator);
            }

            // reset the current stream
            setCurrentStream('');

            // add crash story to history so it's shown
            let tempHistory = [...history];
            tempHistory.push({
                writer: 'ai',
                text: streamAccumulator,
                turn: 'crash',
            });
            setHistory(tempHistory);

            setLoading(true);

            // then - generate the wakeup story
            const wakeupStream = await apiStream({
                method: 'POST',
                url: '/games/initialize_game_wakeup/',
                data: {
                    game_id: gameId,
                    crash_story: streamAccumulator,
                    dev: devMode,
                },
            });

            setLoading(false);

            // reset the current stream
            streamAccumulator = '';
            // stream it in
            for await (const chunk of wakeupStream) {
                // check for an error chunk
                if (chunk === 'CRASH-GAME-INITIALIZATION-ERROR-ABC123') {
                    alert('There was a problem initializing the game - please try again.');
                    // redirect to home
                    window.location.href = '/';
                    return;
                }

                // add chunk to the current stream
                streamAccumulator += chunk;
                setCurrentStream(streamAccumulator);
            }

            // reset current stream
            setCurrentStream('');

            // add it to history
            tempHistory.push({
                writer: 'ai',
                text: streamAccumulator,
                turn: 'wakeup',
            });
            setHistory(tempHistory);

            // then - populate the characters and skills
            populateInfo();

            // then, set the game context to gameIntro
            setGameContext('gameIntro');
        };

        // loads a game
        const loadGame = async () => {
            // stream in the game history
            const loadStream = await apiStream({
                method: 'POST',
                url: '/games/load_game/',
                data: {
                    save_key: saveKey,
                },
            });

            let tempHistory = [];
            let streamAccumulator = '';

            // stream it in
            for await (const chunk of loadStream) {
                // error chunk
                if (chunk === 'CRASH-GAME-LOAD-ERROR-ABC123') {
                    alert('There was a problem retrieving your game - please try again.');
                    // redirect to home
                    window.location.href = '/';
                    return;
                }

                // each chunk is a history item
                // parse it
                // add it to the current stream
                const chunkData = JSON.parse(chunk);

                streamAccumulator = chunkData.text;
                setCurrentStream(streamAccumulator);
                tempHistory.push({
                    writer: chunkData.writer,
                    text: chunkData.text,
                    turn: chunkData.turn,
                });
                setHistory(tempHistory);
            }
            // reset the current stream
            setCurrentStream('');

            // then, populate the characters and skills
            populateInfo();

            // then, set the game context to gameLoaded
            setGameContext('gameLoaded');

            // scroll down
            window.scrollBy({ top: 500, behavior: 'smooth' });
        };

        if (gameContext === 'newGame') {
            initializeGame();
        } else if (gameContext === 'loadGame') {
            loadGame();
        }
    }, []);

    // modal toggles
    const saveKeyModalToggle = () => setSaveKeyModalOpen(!saveKeyModalOpen);
    const charactersModalToggle = () => setCharactersModalOpen(!charactersModalOpen);

    // user submit function
    // handles the logic of the main gameplay
    const handleUserSubmit = async (text) => {
        // if a game has just been loaded and this is the player's
        // first move, then set the game context to gamePlay
        if (gameContext === 'gameLoaded') {
            setGameContext('gamePlay');
        }

        // if this is the player hitting enter after the wakeup story
        if (gameContext === 'gameIntro') {
            // render the loading dots
            setLoading(true);

            // then, make an api call to get the game intro
            const gameIntroStream = await apiStream({
                method: 'POST',
                url: '/games/initialize_game_intro/',
                data: {
                    game_id: gameId,
                },
            });

            // turn off the loading dots
            setLoading(false);

            // stream in the response
            let streamAccumulator = '';
            const words = 500;
            let i = 0;
            for await (const chunk of gameIntroStream) {
                // error handling
                if (chunk === 'CRASH-GAME-INITIALIZATION-ERROR-ABC123') {
                    alert('There was a problem initializing the game - please try again.');
                    // redirect to home
                    window.location.href = '/';
                    return;
                }

                // add chunk to the current stream
                streamAccumulator += chunk;

                // with every word, scroll down
                if (streamAccumulator.split(' ').length > i && i < words) {
                    window.scrollBy({ top: 500, behavior: 'smooth' });
                    i++;
                }

                setCurrentStream(streamAccumulator);
            }

            // clear the current stream
            setCurrentStream('');

            // add intro to history
            let tempHistory = [...history];
            tempHistory.push({
                writer: 'intro',
                text: streamAccumulator,
                turn: 'intro',
            });
            setHistory(tempHistory);

            // then, set the game context to gamePlay
            // so the player can start playing
            setGameContext('gamePlay');
        }
        // otherwise, this is the main gameplay
        else {
            // if a response is still streaming in, don't let them submit
            if (currentStream) {
                alert('Patience...');
                return;
            }

            // update the game turn
            const currentTurn = gameTurn + 1;
            setGameTurn(currentTurn);
            // reset error input
            setInputTextOnError('');

            // render the loading dots
            setLoading(true);

            // add the user text to history
            let tempHistory = [...history];
            tempHistory.push({
                writer: 'user',
                text: text,
                turn: currentTurn,
            });
            setHistory(tempHistory);

            // call the main loop
            const mainLoopStream = await apiStream({
                method: 'POST',
                url: '/games/main_loop/',
                data: {
                    game_id: gameId,
                    history: history,
                    user_input: text,
                    turn: currentTurn,
                    dev: devMode,
                },
            });

            // turn off the loading dots
            setLoading(false);

            // stream in the response
            let streamAccumulator = '';
            const words = 125;
            let i = 0;
            for await (const chunk of mainLoopStream) {
                // error handling
                // if there's an error in the backend, then reset to the last turn
                if (chunk === 'CRASH-GAME-MAIN-LOOP-ERROR-ABC123') {
                    // reset the game turn
                    setGameTurn(currentTurn - 1);

                    // reset the stream
                    streamAccumulator = '';
                    setCurrentStream('');

                    // reset the history
                    tempHistory.pop();
                    setHistory(tempHistory);

                    // reset the user input
                    setInputTextOnError(text);

                    alert('There was a problem on our end - try again please!');
                    return;
                }
                // add chunk to the current stream
                streamAccumulator += chunk;

                // for the first 100 words, scroll down
                if (streamAccumulator.split(' ').length > i && i < words) {
                    window.scrollBy({ top: 500, behavior: 'smooth' });
                    i++;
                }

                setCurrentStream(streamAccumulator);
            }

            // clear the current stream
            setCurrentStream('');

            // add response to history
            tempHistory.push({
                writer: 'ai',
                text: streamAccumulator,
                turn: currentTurn,
            });
            setHistory(tempHistory);
        }
    };

    // render functions
    const renderFooter = () => {
        // if it's a new game or a game in the process of loading, don't render the footer
        if (gameContext === 'newGame' || gameContext === 'loadGame') {
            return null;
        }
        // otherwise, render it
        else {
            return (
                <Footer
                    inputText={inputTextOnError}
                    gameContext={gameContext}
                    onSubmit={(text) => handleUserSubmit(text)}
                    onKeyClick={saveKeyModalToggle}
                    onCharactersClick={charactersModalToggle}
                />
            );
        }
    };

    return (
        <div
            className='container flex-column main-game'
            style={{
                justifyContent: 'flex-start',
                alignItems: 'top',
                height: '100%',
            }}
        >
            {/* render the loading screen if the title is still loading */}
            {!title && <Loading size={'large'} />}

            {/* otherwise, render the header - contains the title */}
            <Header gameContext={gameContext} title={title} />

            {/* go through the history, and render each text box */}
            {history.map((item) => {
                return (
                    <TextBox
                        gameContext={gameContext}
                        writer={item.writer}
                        text={item.text}
                    />
                );
            })}

            {/* render the current stream, if there's anything in it */}
            {currentStream && (
                <TextBox
                    gameContext={gameContext}
                    writer={gameContext === 'gameIntro' ? 'intro' : 'ai'}
                    text={currentStream}
                />
            )}
            {/* otherwise, render the loading dots */}
            {loading && <Loading size={'small'} />}

            {/* render the footer */}
            {renderFooter()}

            {/* modals */}
            {saveKeyModalOpen && (
                <SaveKeyModal saveKey={saveKey} toggle={saveKeyModalToggle} />
            )}
            {charactersModalOpen && (
                <CharactersModal
                    characters={characters}
                    skillDescriptions={skills}
                    toggle={charactersModalToggle}
                />
            )}
        </div>
    );
};

export default Game;

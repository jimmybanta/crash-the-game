import React, { useEffect, useState, useRef, useReducer } from 'react';

import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';
import CharactersModal from '../Components/CharactersModal';
import Header from '../Components/Header';
import Footer from '../Components/Footer';
import Loading from '../Components/Loading';

import { apiCall, apiStream } from '../api';
import { BASE_URL } from '../BaseURL';
import { cleanup } from '@testing-library/react';


// set our game state with a reducer
const initialState = {
    currentStream: '',
    history: [],
    gameTurn: 1,
    scrollWord: 0,
};
const reducer = (state, action) => {
    switch (action.type) {
        case 'setCurrentStream':
            return { ...state, currentStream: action.payload };
        case 'clearCurrentStream':
            return { ...state, currentStream: '' };
        case 'appendCurrentStream':
            return { ...state, currentStream: state.currentStream + action.payload };
        case 'appendHistory':
            return { ...state, history: [...state.history, action.payload] };
        case 'popHistory':
            let tempHistory = [...state.history];
            tempHistory.pop();
            return { ...state, history: tempHistory };
        case 'setGameTurn':
            return { ...state, gameTurn: action.payload };
        case 'nextTurn':
            return { ...state, gameTurn: state.gameTurn + 1 };
        case 'previousTurn':    
            return { ...state, gameTurn: state.gameTurn - 1 };
        case 'incrementScrollWord':
            return { ...state, scrollWord: state.scrollWord + 1 };
        case 'resetScrollWord':
            return { ...state, scrollWord: 0 };
    }
};

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
    const gameId = props.gameId;
    const saveKey = props.saveKey;
    const theme = props.theme;
    const timeframe = props.timeframe;
    const details = props.details;

    // game content
    // these just get set once
    const [title, setTitle] = useState(props.title ? props.title : '');
    const [characters, setCharacters] = useState([]);
    const [skills, setSkills] = useState([]);

    // game state
    const [state, dispatch] = useReducer(reducer, initialState);
    
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

    // need to use refs to keep track of current stream, gameContext, and gameTurn
    // as they get used in useEffects, or I need them changed and called in the same function
    const gameContextRef = useRef(gameContext);
    const currentStreamRef = useRef(state.currentStream);
    const gameTurnRef = useRef(state.gameTurn);
    const scrollWordRef = useRef(state.scrollWord);
    useEffect(() => { gameContextRef.current = gameContext; }, [gameContext]);
    useEffect(() => { currentStreamRef.current = state.currentStream; }, [state.currentStream]);
    useEffect(() => { gameTurnRef.current = state.gameTurn; }, [state.gameTurn]);
    useEffect(() => { scrollWordRef.current = state.scrollWord; }, [state.scrollWord]);
    

    // make sure gameTurn is set correctly on first render
    useEffect(() => {
        dispatch({ type: 'setGameTurn', payload: props.gameTurn });
    }, [props.gameTurn]);

    // event stream 
    useEffect(() => {
        // Initialize EventSource
        const eventSource = new EventSource(`${BASE_URL}games/stream/${gameId}/`);

        // Handle incoming messages
        eventSource.onmessage = (event) => {
            // turn off the loading dots
            setLoading(false);
            const chunk = JSON.parse(event.data);

            // if we're loading the game, then chunks are dictionaries
            if (gameContextRef.current === 'loadGame') {

                if (chunk.item) {
                    // set the current stream to the text
                    //dispatch({ type: 'setCurrentStream', payload: chunk.item.text });
                    // add the chunk to history
                    dispatch({ type: 'appendHistory', payload: {
                        writer: chunk.item.writer,
                        text: chunk.item.text,
                        turn: chunk.item.turn,
                    
                    } });
                }

            }
            // otherwise, chunks are just text
            else {
                if (chunk.text) {
                    // add chunk to the current stream
                    dispatch({ type: 'appendCurrentStream', payload: chunk.text });

                    // wordsDict gives the number of words to scroll by
                    // scroll depends on game context
                    // i.e. it will scroll for the entire intro
                    // but only 150 words for a main response - so it doesn't go out of view
                    // just want to make it easier on the user
                    const wordsDict = {
                        'newGame': 0,
                        'loadGame': 0,
                        'gameLoaded': 0,
                        'gameIntro': 1000,
                        'gamePlay': 100,
                    }
                    // scroll
                    if ((currentStreamRef.current.split(' ').length > scrollWordRef.current) && 
                        (scrollWordRef.current < wordsDict[gameContextRef.current])) {
                        console.log('scrolling', scrollWordRef.current);
                        window.scrollBy({ top: 500, behavior: 'smooth' });
                        dispatch({ type: 'incrementScrollWord' });
                    }
                }
            }
        };

        // Handle connection open
        eventSource.onopen = () => {
            console.log('Connection to server opened.');
        };

        // Cleanup on component unmount
        return () => {
            eventSource.close();
        };
    }, []);

    // called at the end of a response stream
    const cleanupStream = (turn, writer='ai') => {

        // add stream to history
        dispatch({ type: 'appendHistory', payload: {
            writer: writer,
            text: currentStreamRef.current,
            turn: turn,
        } });

        // reset the current stream
        dispatch({ type: 'clearCurrentStream' });
    };

    // called when there's an error in the response stream
    const handleRespError = (success, resp, text=null) => {

        // if the error occurs while initializaing a game, 
        // introducing it,
        // or loading it
        // then alert the user and redirect to home
        if (gameContextRef.current === 'newGame' || 
            gameContextRef.current === 'loadGame' || 
            gameContextRef.current === 'gameIntro') {
            if (!success) {
                alert(resp);
                // redirect to home
                window.location.href = '/';
                return;
            }

        }
        // if the error occurs while in the main gameplay
        // then reset the turn, and return false
        if (!success) {
            // reset the game turn
            dispatch({ type: 'previousTurn' });

            // reset the stream
            dispatch({ type: 'clearCurrentStream' });

            // reset the history
            dispatch({ type: 'popHistory' });

            // reset the user input
            setInputTextOnError(text);

            alert('There was a problem on our end - try again please!');
            return false;
        }
        return true;
    };

    // auto-scroll
    // run when currentStream or loading changes
    useEffect(() => {
        // if we're loading a game (or a game has loaded), scroll to the bottom of the last textbox
        if (gameContextRef.current === 'loadGame' || gameContextRef.current === 'gameLoaded') {
            window.scrollBy({ top: 500, behavior: 'instant' });
        }

        // if the user has just submitted input, scroll so the loading dots are visible
        if (loading && !(gameContextRef.current === 'newGame')) {
            window.scrollBy({ top: 500, behavior: 'smooth' });
        }
    }, [state.currentStream, loading]);

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
            // handle errors
            handleRespError(titleSuccess, titleResp);

            // set the title so it gets displayed
            setTitle(titleResp.title);


            // then - generate the crash story
            const [crashSuccess, crashResp] = await apiCall({
                method: 'post',
                url: '/games/initialize_game_crash/',
                data: {
                    game_id: gameId,
                    dev: devMode,
                },
            });
            // handle errors
            handleRespError(crashSuccess, crashResp);

            const crashStory = crashResp.crash_story;

            // cleanup the stream
            cleanupStream('crash');


            // render the loading dots
            setLoading(true);

            // then - generate the wakeup story
            const [wakeupSuccess, wakeupResp] = await apiCall({
                method: 'post',
                url: '/games/initialize_game_wakeup/',
                data: {
                    game_id: gameId,
                    crash_story: crashStory,
                    dev: devMode,
                },
            });
            // handle errors
            handleRespError(wakeupSuccess, wakeupResp);

            // cleanup the stream
            cleanupStream('wakeup');

            // then - populate the characters and skills
            populateInfo();

            // then, set the game context to gameIntro
            setGameContext('gameIntro');
        };

        // loads a game
        const loadGame = async () => {
            // get the game history
            const [loadSuccess, loadResp] = await apiCall({
                method: 'post',
                url: '/games/load_game/',
                data: {
                    game_id: gameId,
                    save_key: saveKey,
                    dev: devMode,
                },
            });
            // handle errors
            handleRespError(loadSuccess, loadResp);

            // then, populate the characters and skills
            populateInfo();

            // then, set the game context to gameLoaded
            setGameContext('gameLoaded');

            // scroll down
            window.scrollBy({ top: 500, behavior: 'smooth' });
        };

        if (gameContextRef.current === 'newGame') {
            initializeGame();
        } else if (gameContextRef.current === 'loadGame') {
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
        if (gameContextRef.current === 'gameLoaded') {
            setGameContext('gamePlay');
        }

        // reset the scroll word counter
        dispatch({ type: 'resetScrollWord' });

        // if this is the player hitting enter after the wakeup story
        if (gameContextRef.current === 'gameIntro') {

            if (currentStreamRef.current) {
                alert('Patience...');
                return;
            }
            // render the loading dots
            setLoading(true);

            // then, make an api call to get the game intro
            const [introSuccess, intoResp] = await apiCall({
                method: 'post',
                url: '/games/initialize_game_intro/',
                data: {
                    game_id: gameId,
                    dev: devMode,
                },
            });
            // handle errors
            handleRespError(introSuccess, intoResp);

            // cleanup the stream
            cleanupStream('intro', 'intro');

            // then, set the game context to gamePlay
            // so the player can start playing
            setGameContext('gamePlay');
        }
        // otherwise, this is the main gameplay
        else {
            // if a response is still streaming in, don't let them submit
            if (currentStreamRef.current) {
                // reset the user input
                setInputTextOnError(text);
                alert('Patience...');
                return;
            }

            // increment the game turn
            dispatch({ type: 'nextTurn' });

            // reset error input
            setInputTextOnError('');

            // render the loading dots
            setLoading(true);

            // add the user text to history
            dispatch({ type: 'appendHistory', payload: {
                writer: 'user',
                text: text,
                turn: gameTurnRef.current,
            } });

            // then, make an api call to get the AI response
            const [mainLoopSuccess, mainLoopResp] = await apiCall({
                method: 'post',
                url: '/games/main_loop/',
                data: {
                    game_id: gameId,
                    user_input: text,
                    history: state.history,
                    turn: gameTurnRef.current,
                    dev: devMode,
                },
            });
            if (!mainLoopSuccess) {
                // handle errors
                handleRespError(mainLoopSuccess, mainLoopResp, text);
                return;
            }
            // cleanup the stream
            cleanupStream(state.gameTurn);
        }
    };

    // render functions
    const renderFooter = () => {
        // if it's a new game or a game in the process of loading, don't render the footer
        if (gameContextRef.current === 'newGame' || 
            gameContextRef.current === 'loadGame') {
            return null;
        }
        // otherwise, render it
        else {
            return (
                <Footer
                    inputText={inputTextOnError}
                    gameContext={gameContextRef.current}
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
            <Header gameContext={gameContextRef.current} title={title} />

            {/* go through the history, and render each text box */}
            {state.history.map((item, index) => {
                return (
                    <TextBox
                        key={index}
                        gameContext={gameContextRef.current}
                        writer={item.writer}
                        text={item.text}
                    />
                );
            })}

            {/* render the current stream, if there's anything in it */}
            {state.currentStream && (
                <TextBox
                    gameContext={gameContextRef.current}
                    writer={gameContextRef.current === 'gameIntro' ? 'intro' : 'ai'}
                    text={state.currentStream}
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

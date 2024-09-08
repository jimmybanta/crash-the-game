import { React, useEffect, useState } from 'react';
import { ReactTyped } from 'react-typed';
import axios from 'axios';


import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';
import CharactersModal from '../Components/CharactersModal';
import Header from '../Components/Header';
import UserText from '../Components/UserText';

import { generateStream } from '../streaming';


const Game = ( props ) => {

    // keeping track of where in the game we are
    /// three phases: 
    // 1. newGame - the game is being initialized
    // 2. gameIntro - the game is being introduced
    // 3. gamePlay - the game is being played
    const [newGame, setNewGame] = useState(props.newGame || false);
    const [gameIntro, setGameIntro] = useState(false);

    // game details
    const [gameId, setGameId] = useState(props.gameId);
    const [saveKey, setSaveKey] = useState(props.saveKey);
    const [theme, setTheme] = useState(props.theme);
    const [timeframe, setTimeframe] = useState(props.timeframe);
    const [details, setDetails] = useState(props.details);

    // game title and content
    const [title, setTitle] = useState('');
    const [history, setHistory] = useState([]);
    const [currentStream, setCurrentStream] = useState('');
    const [characters, setCharacters] = useState([]);
    const [skills, setSkills] = useState([]);

    // modals
    const [saveKeyModalOpen, setSaveKeyModalOpen] = useState(false);
    const [charactersModalOpen, setCharactersModalOpen] = useState(false);

    const [devMode, setDevMode] = useState(props.devMode);

    // if this is a new game, we need to initialize it
    useEffect(() => {

        const initializeGame = async () => {

            if (newGame) {
                // make api call to initialize game

                // first - generate the title
                const titleResp = await axios({
                    method: 'post',
                    url: '/games/initialize_game_title/',
                    data: {
                        game_id: gameId,
                        theme: theme,
                        timeframe: timeframe,
                        details: details,
                        dev: devMode
                    }});

                setTitle(titleResp.data.title);
                
                // then - generate the crash story

                const crashStream = await generateStream(
                    '/games/initialize_game_crash/',
                    { game_id: gameId,
                        dev: devMode
                     }
                );

                // stream it in
                let streamAccumulator = '';
                for await (const chunk of crashStream) {
                    // add chunk to the current stream
                    streamAccumulator += chunk;
                    setCurrentStream(streamAccumulator);
                }

                // reset the current stream
                setCurrentStream('');

                // add crash story to history so it's shown
                let tempHistory = [...history];
                tempHistory.push({
                    'writer': 'ai',
                    'text': streamAccumulator
                });
                setHistory(tempHistory);

                // then - generate the wakeup story
                const wakeupStream = await generateStream(
                    '/games/initialize_game_wakeup/',
                    { game_id: gameId,
                        crash_story: streamAccumulator,
                        dev: devMode
                     }
                );

                // reset the current stream
                streamAccumulator = '';
                // stream it in
                for await (const chunk of wakeupStream) {
                    // add chunk to the current stream
                    streamAccumulator += chunk;
                    setCurrentStream(streamAccumulator);
                }

                // reset current stream
                setCurrentStream('');

                // add it to history
                tempHistory.push({
                    'writer': 'ai',
                    'text': streamAccumulator
                });
                setHistory(tempHistory);

                

                // then, display the userText component 
                setNewGame(false);
                setGameIntro(true);

                // then, populate the characters
                const charactersResp = await axios({
                    method: 'get',
                    url: '/games/api/characters/',
                    params: {
                        game_id: gameId,
                    }
                });

                setCharacters(charactersResp.data);

                // then, populate the skills
                const skillsResp = await axios({
                    method: 'get',
                    url: '/games/api/skills/',
                    params: {
                        game_id: gameId,
                    }
                });

                setSkills(skillsResp.data);

            }

        };

        initializeGame();
    
    }, []);


    const saveKeyModalToggle = () => {
        setSaveKeyModalOpen(!saveKeyModalOpen);
    };

    const charactersModalToggle = () => {
        setCharactersModalOpen(!charactersModalOpen);
    };

    const test = () => {
        setSaveKeyModalOpen(true);
    };

    const handleUserSubmit = async (text) => {

        if (gameIntro) {
            setGameIntro(false);

            // then, make an api call to get the game intro
            const gameIntroStream = await generateStream(
                '/games/initialize_game_intro/',
                { game_id: gameId,
                 }
            );

            let streamAccumulator = '';
            for await (const chunk of gameIntroStream) {
                // add chunk to the current stream
                // make the chunk italics
                streamAccumulator += chunk;
                setCurrentStream(streamAccumulator);
            }

            // clear the current stream
            setCurrentStream('');

            // add it to history
            let tempHistory = [...history];
            tempHistory.push({
                'writer': 'game_intro',
                'text': streamAccumulator
            });
            setHistory(tempHistory);




        }
        else {

            // add the user text to history
            let tempHistory = [...history];
            tempHistory.push({
                'writer': 'human',
                'text': text
            });
            setHistory(tempHistory);

            // call the main loop
            const mainLoopStream = await generateStream(
                '/games/main_loop/',
                {   game_id: gameId,
                    history: history,
                    user_input: text,
                    dev: devMode
                 }
            );

            let streamAccumulator = '';
            for await (const chunk of mainLoopStream) {
                // add chunk to the current stream
                streamAccumulator += chunk;
                setCurrentStream(streamAccumulator);
            }

            // clear the current stream
            setCurrentStream('');

            // add it to history
            tempHistory.push({
                'writer': 'ai',
                'text': streamAccumulator
            });
            setHistory(tempHistory);
        }

    };

    const renderUserText = () => {

        // if newGame is true, don't display it yet
        if (!newGame) {
            return (
                <UserText 
                gameIntro={gameIntro}
                onSubmit={(text) => handleUserSubmit(text)}
                onKeyClick={saveKeyModalToggle}
                onCharactersClick={charactersModalToggle}/>
            );
        }
        else {
            return null;
        }

    };



    return (
        <div className='container flex-column main-game'
            style={{ 
                    justifyContent: 'flex-start', alignItems: 'top',
                    height: '100%',
            }}>
            {/* render the header - contains the title */}
            <Header newGame={newGame} title={title} />

            {/* go through the history, and render each text box */}
            {history.map((item) => {
                return (
                    <TextBox writer={item.writer} text={item.text} />
                );
            })};

            {/* render the current stream */}
            <TextBox writer={'ai'} text={currentStream}/>


            {/* render the user text input */}
            {renderUserText()}

                {/* <button className='button home-button text'
                onClick={() => test()}>
                    test
                </button> */}

        
        {saveKeyModalOpen && 
            <SaveKeyModal 
            saveKey={saveKey} 
            toggle={saveKeyModalToggle}/>
        }

        {charactersModalOpen &&
            <CharactersModal 
            characters={characters}
            skillDescriptions={skills}
            toggle={charactersModalToggle}
            />
        }

        </div>
    
    )
    }



export default Game;
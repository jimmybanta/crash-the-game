import { React, useEffect, useState, useRef } from 'react';
import { ReactTyped } from 'react-typed';
import axios from 'axios';


import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';
import CharactersModal from '../Components/CharactersModal';
import Header from '../Components/Header';
import Footer from '../Components/Footer';

import { generateStream } from '../streaming';


const Game = ( props ) => {

    // five possible values for gameContext:
    // 1. newGame - a new game is being initialized
    // 2. loadGame - an old game is being loaded
    // 3. gameLoaded - a game has been loaded, and we want to welcome the player back
    // 4. gameIntro - a new game is being introduced to the player
    // 5. gamePlay - the game is being played
    const [gameContext, setGameContext] = useState(props.gameContext);


    // game details
    const [gameId, setGameId] = useState(props.gameId);
    const [saveKey, setSaveKey] = useState(props.saveKey);
    const [theme, setTheme] = useState(props.theme);
    const [timeframe, setTimeframe] = useState(props.timeframe);
    const [details, setDetails] = useState(props.details);

    // game title and content
    const [title, setTitle] = useState(props.title ? props.title : '');
    const [history, setHistory] = useState([]);
    const [currentStream, setCurrentStream] = useState('');
    const [characters, setCharacters] = useState([]);
    const [skills, setSkills] = useState([]);

    // modals
    const [saveKeyModalOpen, setSaveKeyModalOpen] = useState(false);
    const [charactersModalOpen, setCharactersModalOpen] = useState(false);

    const [devMode, setDevMode] = useState(props.devMode);

    const bottomRef = useRef(null);

    // auto-scroll
    useEffect(() => {

        // if we're loading a game (or a game has loaded), scroll to the bottom of the last textbox
        if (gameContext === 'loadGame' || gameContext === 'gameLoaded') {
            console.log('scrolling to bottom');
            bottomRef.current?.scrollIntoView({ behavior: 'instant', block: 'end' });
        }

        // if it's a new game, then don't scroll
        
    }, [currentStream]);

    // initialize/load game
    useEffect(() => {

        const populateInfo = async () => {
            // need to populate the characters and the skills
            console.log(gameId);
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

        };

        const initializeGame = async () => {

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

                // then - populate the characters and skills
                populateInfo();

                // then, set the game context to gameIntro
                setGameContext('gameIntro');

        };

        const loadGame = async () => {

            try {

                // stream in the game history
                const loadStream = await generateStream(
                    '/games/load_game/',
                    { save_key: saveKey, }
                );


                let tempHistory = [];
                let streamAccumulator = '';
    
                // stream it in
                for await (const chunk of loadStream) {
                    // each chunk is a history item
                    // parse it
                    // add it to the current stream
                    const chunkData = JSON.parse(chunk);
                    
                    streamAccumulator = chunkData.text;
                    setCurrentStream(streamAccumulator);
                    tempHistory.push({
                        'writer': chunkData.writer,
                        'text': chunkData.text
                    });
                    setHistory(tempHistory);
                    }
                // reset the current stream
                setCurrentStream('');

                // then, populate the characters and skills
                populateInfo();

                // then, set the game context to gameLoaded
                setGameContext('gameLoaded');

                }



            catch (error) {
                console.log('Error:', error);
            }
            

        };

        

        if (gameContext === 'newGame') {
            initializeGame();
        }
        else if (gameContext === 'loadGame') {
            loadGame();
        }
    
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

        // if a game has just been loaded and this is the player's 
        // first move, then set the game context to gamePlay
        if (gameContext === 'gameLoaded') {
            // then, set the game context to gamePlay
            setGameContext('gamePlay');
        }

        if (gameContext === 'gameIntro') {

            // then, make an api call to get the game intro
            const gameIntroStream = await generateStream(
                '/games/initialize_game_intro/',
                { game_id: gameId,
                 }
            );


            let streamAccumulator = '';
            const words = 50;
            let i = 0;
            for await (const chunk of gameIntroStream) {
                // add chunk to the current stream
                streamAccumulator += chunk;

                // for the first 150 words, scroll down
                if ((streamAccumulator.split(' ').length > i) && (i < words)) {
                    window.scrollBy({ top: 500, behavior: 'smooth' });
                    i++;
                }


                setCurrentStream(streamAccumulator);
            }

            // clear the current stream
            setCurrentStream('');

            // add it to history
            let tempHistory = [...history];
            tempHistory.push({
                'writer': 'intro',
                'text': streamAccumulator
            });
            setHistory(tempHistory);

            // then, set the game context to gamePlay
            setGameContext('gamePlay');


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
            const words = 100;
            let i = 0;
            for await (const chunk of mainLoopStream) {
                // add chunk to the current stream
                streamAccumulator += chunk;

                // for the first 100 words, scroll down
                if ((streamAccumulator.split(' ').length > i) && (i < words)) {
                    window.scrollBy({ top: 500, behavior: 'smooth' });
                    i++;
                }

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

    const renderCurrentStream = () => {

        // if it's a new game, we don't want it to scroll
        if (gameContext === 'newGame') {
            // if there's a current stream, render it
            if (currentStream) {
                return (
                    <TextBox
                    writer={'ai'} 
                    text={currentStream}/>
                )
            } 
            // otherwise, don't render anything
            else {
                return null;
            }
        }

        /* else if (gameContext === 'gamePlay') {
            if (currentStream) {
                return (
                    <div style={{
                        //border: '1px solid white'
                        }}>
                        <div ref={bottomRef} 
                        style={{ 
                            visibility: 'hidden',
                            height: '0px', 
                            userSelect: 'none' }} />
                        <TextBox
                        writer={'ai'} 
                        text={currentStream}/>
                    </div>
                )
            }
            else {
                return null;
            }
        }
 */

        // if we're loading, introducing, or playing a game, we want to scroll
        // loading - scroll to the bottom of the last element
        // introducing or playing - scroll to the top of the last element - so the player can read at their own pace
        // top or bottom will be handled in the useEffect, with the alignToTop value
        else {
            if (currentStream) {
                return (
                    <TextBox
                    writer={'ai'} 
                    text={currentStream}/>
                )
            }
            else {
                return null;
            }
        }


    };

    const renderFooter = () => {

        // if it's a new game or a game in the process of loading, don't render the footer
        if (gameContext === 'newGame' || gameContext === 'loadGame') {
            return null;
        }
        // otherwise, render it
        else {
            return (
                <Footer 
                gameContext={gameContext}
                onSubmit={(text) => handleUserSubmit(text)}
                onKeyClick={saveKeyModalToggle}
                onCharactersClick={charactersModalToggle}/>
            );
        }

    };



    return (
            <div className='container flex-column main-game'
                style={{ 
                        justifyContent: 'flex-start', alignItems: 'top',
                        height: '100%',
                }}>
                {/* render the header - contains the title */}
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
                {/* {renderCurrentStream()} */}
                {currentStream && 
                <TextBox
                gameContext={gameContext}
                writer={(gameContext === 'gameIntro') ? 'intro' : 'ai'} 
                text={currentStream}/>}
                {/* add a div to scroll to */}
                <div ref={bottomRef}
                    style={{ 
                        height: '0px', 
                        userSelect: 'none' }} />


                {/* render the footer */}
                {renderFooter()}

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
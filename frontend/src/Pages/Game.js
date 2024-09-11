import { React, useEffect, useState, useRef } from 'react';
import axios from 'axios';


import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';
import CharactersModal from '../Components/CharactersModal';
import Header from '../Components/Header';
import Footer from '../Components/Footer';
import Loading from '../Components/Loading';

import { generateStream } from '../apiCall';


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

    // auto-scroll ref
    const bottomRef = useRef(null);

    // loading dots
    const [loading, setLoading] = useState(false);

    const [devMode, setDevMode] = useState(props.devMode);

    // auto-scroll
    useEffect(() => {

        // if we're loading a game (or a game has loaded), scroll to the bottom of the last textbox
        if (gameContext === 'loadGame' || gameContext === 'gameLoaded') {
            bottomRef.current?.scrollIntoView({ behavior: 'instant', block: 'end' });
        }

        // if the user has just submitted input, scroll so the loading dots are visible
        if (loading) {
            window.scrollBy({ top: 500, behavior: 'smooth' });
        }
        
    }, [currentStream, loading]);

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

                setLoading(true);

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

                setLoading(true);

                // then - generate the wakeup story
                const wakeupStream = await generateStream(
                    '/games/initialize_game_wakeup/',
                    { game_id: gameId,
                        crash_story: streamAccumulator,
                        dev: devMode
                     }
                );

                setLoading(false);

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

            // render the loading dots
            setLoading(true);

            // then, make an api call to get the game intro
            const gameIntroStream = await generateStream(
                '/games/initialize_game_intro/',
                { game_id: gameId,
                 }
            );

            // turn off the loading dots
            setLoading(false);

            // stream in the response
            let streamAccumulator = '';
            const words = 500;
            let i = 0;
            for await (const chunk of gameIntroStream) {
                // add chunk to the current stream
                streamAccumulator += chunk;

                // with every word, scroll down
                if ((streamAccumulator.split(' ').length > i) && (i < words)) {
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
                'writer': 'intro',
                'text': streamAccumulator
            });
            setHistory(tempHistory);

            // then, set the game context to gamePlay
            // so the player can start playing
            setGameContext('gamePlay');
        }
        else {

            // if a response is still streaming in, don't let them submit
            if (currentStream) {
                alert('Patience...');
                return;
            }

            // render the loading dots
            setLoading(true);            

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

            // turn off the loading dots
            setLoading(false);

            // stream in the response
            let streamAccumulator = '';
            const words = 125;
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

            // add response to history
            tempHistory.push({
                'writer': 'ai',
                'text': streamAccumulator
            });
            setHistory(tempHistory);
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

                {/* render the loading screen if the title is still loading */}
                {title === '' && <Loading size={'large'}/>}

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
                {/* otherwise, render the loading dots */}
                {currentStream && 
                <TextBox
                gameContext={gameContext}
                writer={(gameContext === 'gameIntro') ? 'intro' : 'ai'} 
                text={currentStream}/>
                }

                {loading && <Loading size={'small'}/>}

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
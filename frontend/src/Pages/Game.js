import { React, useEffect, useState } from 'react';
import { ReactTyped } from 'react-typed';
import axios from 'axios';


import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';
import CharactersModal from '../Components/CharactersModal';
import Header from '../Components/Header';
import UserText from '../Components/UserText';

import { generateStream } from '../streaming';


const text = "The snow swirls and drifts, obscuring the icy landscape. Samantha's eyes flutter open as she comes to, her head pounding. She coughs, the frigid air stinging her lungs. \n\n\"Where...where am I?\" she murmurs, disoriented. \n\nLiam is already on his feet, surveying the damage to the plane. \"Looks like we went down hard. That engine failure came out of nowhere.\"\n\nEsteban groans, pulling himself upright in his seat. \"This is...unacceptable. I demand to know how soon we can be rescued.\"\n\nSamantha takes in their surroundings, her brow furrowed. \"I don't think rescue is coming anytime soon. We're in the middle of nowhere.\"\n\nThe group falls silent as they gaze out at the vast, snow-covered expanse. In the distance, a shadowy shape can be seen, half-buried in the drifts.\n\n\"What is that?\" Esteban squints, peering through the blowing snow.\n\nLiam's expression grows grim. \"I don't know, but I have a feeling we're not alone out here.\"\n\nThe characters turn to face the mysterious structure, their breaths forming puffs of vapor in the frigid air. Samantha's eyes are alight with a gleam of scholarly curiosity, even as a hint of trepidation creeps into her voice.\n\n\"We need to investigate. There may be clues, or even a way to signal for help. But...I can't shake the feeling that we're not the first ones to stumble upon this place.\"\n\nThe player is left with a choice - what do they want the characters to do next? Venture out to explore the strange, half-buried structure, or stay put and try to secure the damaged plane? The path forward is uncertain, and the consequences of their actions could have profound implications.";

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

    // modals
    const [saveKeyModalOpen, setSaveKeyModalOpen] = useState(false);
    const [charactersModalOpen, setCharactersModalOpen] = useState(false);

    const [devMode, setDevMode] = useState('false');

    // if this is a new game, we need to initialize it
    useEffect(() => {

        const initializeGame = async () => {

            if (newGame) {
                console.log('initializing new game');
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
                tempHistory.push(streamAccumulator);
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
                tempHistory.push(streamAccumulator);
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
            // first, make an api call to get the characters
            const charactersResp = await axios({
                method: 'get',
                url: '/games/api/characters/',
                params: {
                    game_id: gameId,
                }
            });

            console.log('characters:', charactersResp.data);
            setCharacters(charactersResp.data);

            // then, make an api call to get the game intro
            const gameIntroStream = await generateStream(
                '/games/initialize_game_intro/',
                { game_id: gameId,
                 }
            );

            let streamAccumulator = '';
            for await (const chunk of gameIntroStream) {
                // add chunk to the current stream
                streamAccumulator += chunk;
                setCurrentStream(streamAccumulator);
            }

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
            {history.map((text) => {
                return (
                    <TextBox text={text} />
                );
            })};

            {/* render the current stream */}
            <TextBox text={currentStream} />


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
            toggle={charactersModalToggle}
            />
        }

        </div>
         
    

        

    
    
    )
    }



export default Game;
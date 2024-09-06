import { React, useEffect, useState } from 'react';
import { ReactTyped } from 'react-typed';
import axios from 'axios';


import TextBox from '../Components/TextBox';
import SaveKeyModal from '../Components/SaveKeyModal';

import { generateStream } from '../streaming';

const text = "The snow swirls and drifts, obscuring the icy landscape. Samantha's eyes flutter open as she comes to, her head pounding. She coughs, the frigid air stinging her lungs. \n\n\"Where...where am I?\" she murmurs, disoriented. \n\nLiam is already on his feet, surveying the damage to the plane. \"Looks like we went down hard. That engine failure came out of nowhere.\"\n\nEsteban groans, pulling himself upright in his seat. \"This is...unacceptable. I demand to know how soon we can be rescued.\"\n\nSamantha takes in their surroundings, her brow furrowed. \"I don't think rescue is coming anytime soon. We're in the middle of nowhere.\"\n\nThe group falls silent as they gaze out at the vast, snow-covered expanse. In the distance, a shadowy shape can be seen, half-buried in the drifts.\n\n\"What is that?\" Esteban squints, peering through the blowing snow.\n\nLiam's expression grows grim. \"I don't know, but I have a feeling we're not alone out here.\"\n\nThe characters turn to face the mysterious structure, their breaths forming puffs of vapor in the frigid air. Samantha's eyes are alight with a gleam of scholarly curiosity, even as a hint of trepidation creeps into her voice.\n\n\"We need to investigate. There may be clues, or even a way to signal for help. But...I can't shake the feeling that we're not the first ones to stumble upon this place.\"\n\nThe player is left with a choice - what do they want the characters to do next? Venture out to explore the strange, half-buried structure, or stay put and try to secure the damaged plane? The path forward is uncertain, and the consequences of their actions could have profound implications.";

const Game = ( props ) => {

    const [newGame, setNewGame] = useState(props.newGame || false);

    const [gameId, setGameId] = useState(props.gameId);
    const [saveKey, setSaveKey] = useState(props.saveKey);

    const [theme, setTheme] = useState(props.theme);
    const [timeframe, setTimeframe] = useState(props.timeframe);
    const [details, setDetails] = useState(props.details);

    const [title, setTitle] = useState('');
    const [titleTyped, setTitleTyped] = useState(false);

    const [currentStream, setCurrentStream] = useState('');

    const [saveKeyModalOpen, setSaveKeyModalOpen] = useState(newGame ? true : false);

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
                    }});
                
                console.log(titleResp.data);

                setTitle(titleResp.data.title);
                setNewGame(false);

                // then - generate the crash story

                const crashStream = await generateStream(
                    '/games/initialize_game_crash/',
                    { game_id: gameId }
                );

                let streamAccumulator = '';

                for await (const chunk of crashStream) {
                    console.log(chunk);
                    // add chunk to the current stream
                    streamAccumulator += chunk;
                    setCurrentStream(streamAccumulator);
                }
                  

                

            }

        };

        initializeGame();
    
    }, []);


    const saveKeyModalToggle = () => {
        setSaveKeyModalOpen(!saveKeyModalOpen);
    };

    const test = () => {
        setSaveKeyModalOpen(true);
    };

    const initializeGame = () => {
        console.log('initializing game');

    };

    // function for rendering the title, based on 
    const renderTitle = () => {

        // if the save key modal is open, at first, don't render the title yet
        if (newGame && saveKeyModalOpen) {
            return;
        }
        // if the title is not typed yet, render the typing effect
        else if (newGame && !saveKeyModalOpen) {
            return (
                <div className='text title'>
                    <ReactTyped
                        strings={[title]}
                        typeSpeed={20}
                        showCursor={false}
                    />
                </div>
            );
        } 
        // if we're not at the start of the game, just render the title
        else if (!newGame) {
            return (
                <div className='text title'>
                    {title}
                </div>
            );
        }
    };



    return (
        <div className='container flex-column'
            style={{ 
                    justifyContent: 'flex-start', alignItems: 'top',
                    height: '100%', width: '100%',
                    textAlign: 'center', 
                    border: '1px green solid',
            }}>
            {renderTitle()}
            <p className='text'>{currentStream}</p>
                        
            



                <button className='button home-button text'
                onClick={() => test()}>
                    test
                </button>

    

        
        {saveKeyModalOpen && 
            <SaveKeyModal 
            saveKey={saveKey} 
            toggle={saveKeyModalToggle}/>
        }

        </div>
         
    

        

    
    
    )
    }



export default Game;
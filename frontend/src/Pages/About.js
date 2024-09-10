import { React, useState, useEffect } from 'react';
import axios from 'axios';



const About = ({ onSetCurrentPage }) => {

    const [gameVersion, setGameVersion] = useState(null);

    useEffect(() => {

        const getGameVersion = async () => {

            // make a call to the backend to get the current version of the game

            try {

                // first, get the game info
                const gameVersionResp = await axios({
                    method: 'get',
                    url: '/games/get_current_version/',
                });

                setGameVersion(gameVersionResp.data.version);
            }
            catch (error) {
                // if it doesn't work, then leave gameVersion at null
                setGameVersion(null);
            }

        
    };

    getGameVersion();


    }, []);

    return (
        <div className='container flex-column'
        style={{ justifyContent: 'center', alignItems: 'center',
                height: '100%', 
                width: '100%',
        }}>

            <div className='container flex-column' 
            style={{ width: '100%', 
            height: '30%', 
            marginBottom: '3%',
            }}>
                <h1 className='text about-header'>About</h1>
            </div>


            <div className='container flex-column'
            style={{ width: '100%', height: '66%'}}>

                <div className='text about-paragraphs'>
                    Crash is an AI-generated, interactive story game developed by Jimmy Banta.
                </div>

                <div className='text about-paragraphs'>
                    You can see more of his work at <a 
                    href='https://jimmybanta.com'
                    target='_blank'
                    rel='noreferrer'
                    >
                        here
                    </a>.
                </div>

                <div className='text about-paragraphs'>
                    Or you can check out the code for Crash <a 
                    href='https://github.com/jimmybanta/crash-the-game/'
                    target='_blank'
                    rel='noreferrer'
                    >
                        here
                    </a>.
                </div>



                {gameVersion && <div className='text about-paragraphs'>
                    Current version: {gameVersion}
                </div>}

                <div
                className='button back-button text'
                onClick={() => onSetCurrentPage('Home')}>
                    Back
                </div>



            </div>



        </div>
    )
    }



export default About;
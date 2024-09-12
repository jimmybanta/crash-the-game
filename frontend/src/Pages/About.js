import React, { useState, useEffect } from 'react';

import { apiCall } from '../api';

const About = ({ onSetCurrentPage }) => {
    // The about page

    // The current game version
    const [gameVersion, setGameVersion] = useState(null);

    useEffect(() => {
        const getGameVersion = async () => {
            // Make a call to the backend to get the current version of the game
            const [success, resp] = await apiCall({
                method: 'get',
                url: '/games/get_current_version/',
            });

            if (!success) {
                return;
            }

            setGameVersion(resp.version);
        };

        getGameVersion();
    }, []);

    return (
        <div
            className='container flex-column'
            style={{
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                width: '100%',
            }}
        >
            <div
                className='container flex-column'
                style={{
                    width: '100%',
                    height: '30%',
                    marginBottom: '3%',
                }}
            >
                <h1 className='text about-header'>About</h1>
            </div>

            <div className='container flex-column' style={{ width: '100%', height: '66%' }}>
                <div className='text about-paragraphs'>
                    Crash is an AI-generated, interactive story game developed by Jimmy Banta.
                </div>

                <div className='text about-paragraphs'>
                    You can see more of his work {' '}
                    <a className='about-link'
                    href='https://jimmybanta.com' target='_blank' rel='noreferrer'>
                        here
                    </a>
                    .
                </div>

                <div className='text about-paragraphs'>
                    Or you can check out the code for Crash{' '}
                    <a className='about-link'
                    href='https://github.com/jimmybanta/crash-the-game/' target='_blank' rel='noreferrer'>
                        here
                    </a>
                    .
                </div>

                {gameVersion && (
                    <div className='text about-paragraphs'>Current version: {gameVersion}</div>
                )}

                <div className='button back-button text' onClick={() => onSetCurrentPage('Home')}>
                    Back
                </div>
            </div>
        </div>
    );
};

export default About;

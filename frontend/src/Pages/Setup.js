import React, { useState } from 'react';

import { apiCall } from '../api';

const Setup = ({ onSetCurrentPage, onSubmit }) => {
    // a component used to set up a new game

    // game info
    const [theme, setTheme] = useState('');
    const [timeframe, setTimeframe] = useState('');
    const [details, setDetails] = useState('');

    const handleRandomSetup = async () => {

        // make an API call to get a random setup
        const [success, resp] = await apiCall({
            method: 'get',
            url: '/games/random_setup/',
        });

        if (!success) {
            alert('Something went wrong - please try again.');
            return;
        }

        setTheme(resp.theme);
        setTimeframe(resp.timeframe);
        setDetails(resp.details);
    };

    // game info submission
    const handleSubmit = () => {
        onSubmit(theme, timeframe, details);
    };

    return (
        <div
            className='container flex-column'
            style={{
                height: '100%',
                width: '90%',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '2%',
            }}
        >
            <div className='container flex-column' style={{ width: '75%', margin: '3%' }}>
                <h1 className='text setup-input-header'>Choose a theme for your story :</h1>
                <input
                    className='setup-input'
                    type='text'
                    placeholder='pirates, princesses, postpartum depression - anything goes!'
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                />
            </div>

            <div className='container flex-column' style={{ width: '75%', margin: '3%' }}>
                <h1 className='text setup-input-header'>and a timeframe :</h1>
                <input
                    className='setup-input'
                    type='text'
                    placeholder='the distant past, the far future, anywhere in between'
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                />
            </div>

            <div className='container flex-column' style={{ width: '75%', margin: '3%', marginBottom: '1%' }}>
                <h1 className='text setup-input-header'>any details to include ?</h1>
                <input
                    className='setup-input'
                    type='text'
                    placeholder='whatever your beautiful mind can think of'
                    value={details}
                    onChange={(e) => setDetails(e.target.value)}
                />
            </div>

            {/* buttons */}
            <div className='button setup-for-me-button text' style={{ marginTop: '2%' }} onClick={() => handleRandomSetup()}>
                setup for me
            </div>

            <div className='button home-button text' style={{ marginTop: '3%' }} onClick={() => handleSubmit()}>
                Let's Play!
            </div>

            <div className='button back-button text' style={{ marginTop: '3%' }} onClick={() => onSetCurrentPage('Home')}>
                Back
            </div>
        </div>
    );
};

export default Setup;

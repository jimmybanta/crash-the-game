import React, { useState, useEffect } from 'react';

const MIN_API_CALL_INTERVAL = 10000;

const Footer = ({ inputText, gameContext, onSubmit, onKeyClick, onCharactersClick }) => {
    // a component that sits along the bottom
    // where the user can input their commands
    // and see the characters and save key buttons

    const [lastApiCallTime, setLastAPICallTime] = useState(null);

    const [inputValue, setInputValue] = useState(inputText);

    useEffect(() => {
        setInputValue(inputText);
    }, [inputText]);

    // placeholder for the user input
    let placeholder = '';

    // set the placeholder based on the game context
    if (gameContext === 'gameIntro') {
        placeholder = "Type 'continue', then press enter...";
    } else if (gameContext === 'gameLoaded') {
        placeholder = 'Welcome back! what would you like to do next?';
    } else {
        placeholder = 'What do you want to do?';
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {

            // check if the user is trying to spam the API
            if (lastApiCallTime) {
                const currentTime = new Date().getTime();
                const timeSinceLastCall = currentTime - lastApiCallTime;

                if (timeSinceLastCall < MIN_API_CALL_INTERVAL) {
                    return;
                }
        }
        onSubmit(inputValue);
        setInputValue('');
        setLastAPICallTime(new Date().getTime());
    }
};

    const renderButtons = () => {
        if (gameContext === 'gamePlay' || gameContext === 'gameLoaded') {
            return (
                <div>
                    <button
                        className='button home-button text main-game-button-text'
                        style={{ position: 'fixed', bottom: '80px', right: '20px' }}
                        onClick={onCharactersClick}
                    >
                        Characters
                    </button>
                    <button
                        className='button home-button text main-game-button-text'
                        style={{ position: 'absolute', bottom: '20px', right: '20px' }}
                        onClick={onKeyClick}
                    >
                        Save Key
                    </button>
                </div>
            );
        } else {
            return null;
        }
    };

    return (
        <div className='edge-container footer-container'>
            <input
                className='user-text user-input'
                placeholder={placeholder}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => handleKeyPress(e)}
            />
            {renderButtons()}
        </div>
    );
};

export default Footer;

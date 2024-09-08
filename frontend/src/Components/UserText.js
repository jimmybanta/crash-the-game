import { React, useState, useEffect } from 'react';



const UserText = ({ gameIntro, onSubmit, onKeyClick, onCharactersClick }) => {
    // basically a footer, the place where the user can type in their text

    const [inputValue, setInputValue] = useState('');

    let placeholder = 'type here...';

    if (gameIntro) {
        placeholder = "type 'continue', then press enter...";
    }
    else {
        placeholder = 'what do you want to do?';
    }

    const handleKeyPress = (e) => {

        if (e.key === 'Enter') {
            onSubmit(inputValue);
            setInputValue('');
        }

    };

    const renderButtons = () => {

        if (!gameIntro) {
            return (
                <div>
                    <button 
                    className='button home-button text paragraphs'
                    style={{ position: 'fixed', bottom: '80px', right: '20px' }}
                    onClick={onCharactersClick}>
                        Characters
                    </button>
                    <button 
                    className='button home-button text paragraphs'
                    style={{ 
                        position: 'absolute', bottom: '20px', right: '20px' }}
                    onClick={onKeyClick}>
                        Key
                    </button>
                </div>
            )
        }
        else {
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

export default UserText;
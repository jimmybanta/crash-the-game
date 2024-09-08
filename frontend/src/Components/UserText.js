import { React, useState, useEffect } from 'react';



const UserText = ({ gameIntro, onSubmit }) => {
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


    return (
        <div className='edge-container footer-container'>
            <input
            className='user-text user-input'
            placeholder={placeholder}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => handleKeyPress(e)}
            
            />
            
        
        </div>
    );

};

export default UserText;
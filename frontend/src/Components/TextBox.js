import React, { useState, useEffect } from 'react';

const TextBox = ({ gameContext, writer, text }) => {

    // there are three options for writer
    // 'user' - the user
    // 'ai' - the AI
    // 'intro' - the intro text

    // ai text shouldn't be italicized
    // user text & intro text should be italicized
    const [italicize, setItalicize] = useState(writer === 'ai' ? false : true);

    const [collapsed, setCollapsed] = useState(false);

    // if we're in the game loading phase, then collapse all the AI & intro text
    useEffect(() => {

        if (gameContext === 'gameLoaded' || gameContext === 'loadGame') {
            if (writer === 'ai' || writer === 'intro') {
                setCollapsed(true);
            }
        }
        
    }, [gameContext]);

    const handleCollapse = () => {
        setCollapsed(!collapsed);
    };

    const renderText = () => {
        if (collapsed) {
            // show only the first 15 words
            return text.split(' ').slice(0, 15).join(' ') + '...';
        }
        return text;
    };

    return (
        <div
            className='container text paragraphs'
            style={{
                textAlign: writer === 'ai' || writer === 'intro' ? 'left' : 'right',
                whiteSpace: 'pre-wrap',
                position: 'relative',
                cursor: 'pointer',
                marginBottom: '5%',
            }}
            onClick={handleCollapse}
        >
            <p
                style={{
                    opacity: collapsed ? '.6' : '1',
                    fontStyle: italicize ? 'italic' : 'normal',
                }}
            >
                {renderText()}
            </p>
        </div>
    );
};

export default TextBox;

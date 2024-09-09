
import { React, useState, useEffect } from 'react';
import { ReactTyped } from 'react-typed';


const TextBox = ({ gameContext, writer, text }) => {

    // there are three options for writer
    // 'human' - the user
    // 'ai' - the AI
    // 'intro' - the intro text

    //const [showArrow, setShowArrow] = useState(false);
    const [collapsed, setCollapsed] = useState(false);

    const [italicize, setItalicize] = useState((writer === 'ai') ? false : true);
    

    // if the text starts with '<i>', then italicize it
    useEffect(() => {
        try {
            if (text.startsWith('<i>')) {
                text = text.slice(3);
                setItalicize(true);
            };
        }
        catch (error) {
            console.log('Error:', error);
            console.log('Text:', text);
        }
    }, [text]);

    useEffect(() => {
        // if we're in the gameLoaded phase, then collapse all the AI & intro text

        if (gameContext === 'gameLoaded' || gameContext === 'loadGame') {
            if (writer === 'ai' || writer === 'intro') {
                setCollapsed(true);
            }
        }
    }, [gameContext]);


    /* useEffect(() => {
        // Set a timeout to show the arrow, and stop the text from being typed again,
        // after the text is done typing
        const timeoutId = setTimeout(() => {
            setShowArrow(true);
        }, 1000); // Adjust the timeout duration as needed

        // Cleanup the timeout if the component unmounts
        return () => clearTimeout(timeoutId);
    }, []);

    const handleArrowClick = () => {
        setCollapsed(!collapsed);
    };

    // currently unused - if we want arrows to show up on the left side
    const renderArrow = () => {
        if (showArrow) {
            return (
                <div 
                    className='text'
                    style={{ position: 'absolute', left: '-100px', top: '15px' }}
                >
                    <div>
                        {collapsed ? '▶' : '▼'}
                    </div>
                </div>
            );
        }
        return null;
    }; */

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
        <div className='container text paragraphs'
            style={{ 
                textAlign: (writer === 'ai' || writer === 'intro') ? 'left' : 'right',
                whiteSpace: 'pre-wrap', position: 'relative',
                cursor: 'pointer',
                marginBottom: '5%',
                //border: '1px solid red',
                //overflow: 'auto'
            }}
            onClick={handleCollapse}
        >
            <p 
                style={{ opacity: collapsed ? '.6' : '1',
                        fontStyle: italicize ? 'italic' : 'normal',
                }}
            >
                {renderText()}
            </p>
            {/* {renderArrow()} */}
        </div>
    )
}

export default TextBox;
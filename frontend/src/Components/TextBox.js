
import { React, useState, useEffect } from 'react';
import { ReactTyped } from 'react-typed';


const TextBox = ({ text }) => {

    const [showArrow, setShowArrow] = useState(false);
    const [collapsed, setCollapsed] = useState(false);

    useEffect(() => {
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
                textAlign: 'left', 
                whiteSpace: 'pre-wrap', position: 'relative',
                cursor: 'pointer',
                marginBottom: '5%',
                //border: '1px solid red',
                //overflow: 'auto'
            }}
            onClick={handleArrowClick}
        >
            <p 
            style={{ opacity: collapsed ? '.6' : '1' }}>
                {renderText()}
            </p>
            {/* {renderArrow()} */}
        </div>
    )
}

export default TextBox;
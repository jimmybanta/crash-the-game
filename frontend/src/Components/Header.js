import React from 'react';
import { ReactTyped } from 'react-typed';



const Header = ({ gameContext, title }) => {
    // a header that renders the Title of the game

    // function for rendering the title, based on the game context
    const renderTitle = () => {

        // if this is a new game or loading a game, then type out the title
        if (gameContext === 'newGame' || gameContext === 'loadGame') {
            return (
                <div className='container'>
                    <div className='text title'>
                        <ReactTyped
                            strings={[title]}
                            typeSpeed={20}
                            showCursor={false}
                        />
                    </div>
                </div>
            );
        }
        // otherwise, just display the title
        else {
            return (
                <div className='text title'>
                    {title}
                </div>
            );
        }
    };

    return (
        <div className='header edge-container header-container'>
            {renderTitle()}
        </div>
    );
};


export default Header;
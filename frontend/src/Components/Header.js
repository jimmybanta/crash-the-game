import { React, useState } from 'react';
import { ReactTyped } from 'react-typed';



const Header = ({ newGame, title}) => {

    // function for rendering the title, based on 
    const renderTitle = () => {

        // if this is a new game, then type out the title
        if (newGame) {
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
        // if we're not at the start of the game, just render the title
        else if (!newGame) {
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
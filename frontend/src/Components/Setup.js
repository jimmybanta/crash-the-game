

import { React, useState } from 'react';


// A component that will be used to set up a new game.
const Setup = ({ onSubmit }) => {

    const [theme, setTheme] = useState('');
    const [timeframe, setTimeframe] = useState('');
    const [details, setDetails] = useState('');
    


    const handleSubmit = () => {
        // Handle form submission logic here
        onSubmit(theme, timeframe, details);
      };


    return (
        <div className='container flex-column'
        style={{ height: '90%', width: '90%', 
            border: '1px white solid',
            justifyContent: 'center', alignItems: 'center',
            gap: '2%'
        }}>

            <div className='container flex-column' style={{width: '75%'}}>
                <h1 className='text setup-input-header'>Choose a theme for your story :</h1>
                <input className='setup-input'
                    type='text'
                    placeholder='pirates, princesses, post-partem depression - anything goes!'
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                />
            </div>

            <div className='container flex-column' style={{width: '75%'}}>
                <h1 className='text setup-input-header'>and a timeframe :</h1>
                <input className='setup-input'
                    type='text'
                    placeholder='the distant past, the far future, anywhere in between'
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                />
            </div>

            <div className='container flex-column' style={{width: '75%'}}>
                <h1 className='text setup-input-header'>any added details to include ?</h1>
                <input className='setup-input'
                    type='text'
                    placeholder='whatever your beautiful mind can think of'
                    value={details}
                    onChange={(e) => setDetails(e.target.value)}
                />
            </div>

            <div 
            className='home-button text'
            style={{marginTop: '3%'}}
            onClick={() => handleSubmit()}>
                Let's Play!
            </div>
        </div>
    )


};

export default Setup;
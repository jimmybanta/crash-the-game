
import { React, useState } from 'react';

import Setup from '../Components/Setup';



const NewGame = () => {

    const [setupComplete, setSetupComplete] = useState(false);



    return (
    <div className='container flex-column'
        style={{ justifyContent: 'flex-start', alignItems: 'top',
                height: '90%', width: '80%',
                textAlign: 'center', 
                border: '1px white solid',
        }}>

        <div className='container flex-column'
            style={{ height: '100%', width: '100%', 
                justifyContent: 'center', alignItems: 'center'}}
        >
            { !setupComplete && <Setup />}
        </div>
        

            
         
    </div>
    )

};

export default NewGame;

import { React } from 'react';
import { ReactTyped } from 'react-typed';


const TextBox = ({ text }) => {



    return (
        <div className='container text'
        style={{ display: 'flex', flexDirection: 'column', 
                justifyContent: 'center', alignItems: 'center',
                textAlign: 'left', 
                border: '1px white solid',
                fontSize: '3em',
        }}
        >
            <p>
                <ReactTyped
                    strings={[text]}
                    typeSpeed={1}
                    showCursor={true}
                />
                
            </p>
        </div>
    )
}

export default TextBox;
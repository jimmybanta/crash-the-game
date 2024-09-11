

import { React, useState } from 'react';



const Loading = ({ size }) => {

    // maybe make it responsive to container size, or we can pass in font size
    // so we can use it in multiple contexts?

    const fontClass = (size === 'large') ? 'text header': 'text loading-dots';


    return (
        <div className='container flex-row'
        style={{ justifyContent: (size === 'large') ? 'center': 'flex-start',
            paddingBottom: '20px'
        }}>
            <div className={fontClass}>
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
            </div>
        </div>
    )


};

export default Loading;
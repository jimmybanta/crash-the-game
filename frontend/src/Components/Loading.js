

import { React, useState } from 'react';



const Loading = ({ fontSize }) => {

    // maybe make it responsive to container size, or we can pass in font size
    // so we can use it in multiple contexts?


    return (
        <div className='container flex-row'>
            <div className='text header'>
                Loading
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
            </div>
        </div>
    )


};

export default Loading;
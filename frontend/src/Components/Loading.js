import React from 'react';


const Loading = ({ size }) => {
    // Loading dots
    
    const fontClass = (size === 'large') ? 'text header': 'text loading-dots';

    return (
        <div className='container flex-row'
            style={{
                //justifyContent: (size === 'large') ? 'center' : 'flex-start',
                justifyContent: 'center',
                paddingBottom: '20px'
            }}
        >
            <div className={fontClass}>
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
            </div>
        </div>
    )


};

export default Loading;
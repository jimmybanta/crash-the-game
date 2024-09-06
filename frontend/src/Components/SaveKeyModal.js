
import { 
    Modal, ModalHeader, 
    ModalBody, ModalFooter,
} from "reactstrap";

import { React, useRef } from "react";


const SaveKeyModal = ({ toggle, saveKey }) => {

    const keyRef = useRef(null);

    const handleKeyClick = () => {
        const range = document.createRange();
        range.selectNodeContents(keyRef.current);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    };

    return (
    <Modal 
    centered
    isOpen={true}
    toggle={toggle}>
        <ModalHeader style={{userSelect: 'none'}}>
            Save Key
        </ModalHeader>
        <ModalBody>
            <p style={{userSelect: 'none'}}>
                Here is your save key. Keep it somewhere safe! This is how you can load a game later on.
            </p>
            <pre ref={keyRef} onClick={handleKeyClick} style={{ cursor: 'pointer', backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '5px' }}>
                    {saveKey}
                </pre>
        </ModalBody>
        <ModalFooter>
            <div className='button modal-button' 
                onClick={toggle}>Done</div>
        </ModalFooter>
    </Modal>
    );


};


export default SaveKeyModal;
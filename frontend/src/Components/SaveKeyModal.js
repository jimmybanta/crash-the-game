import {
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
} from "reactstrap";

import React, { useRef } from "react";

const SaveKeyModal = ({ toggle, saveKey }) => {
    // modal for displaying the save key

    const keyRef = useRef(null);

    // when the user clicks the save key, highlight the whole thing
    // so it's easy to copy
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
            toggle={toggle}
        >
            <ModalHeader
                className='modal-text'
                style={{ userSelect: 'none' }}
            >
                Save Key
            </ModalHeader>
            <ModalBody>
                <p
                    className='modal-text'
                    style={{ userSelect: 'none' }}
                >
                    Here is your save key. Keep it somewhere safe! This is how you can load a game later on.
                </p>
                <pre
                    className='save-key-text'
                    ref={keyRef}
                    onClick={handleKeyClick}
                    style={{
                        cursor: 'pointer',
                        backgroundColor: '#f8f9fa',
                        padding: '10px',
                        borderRadius: '5px'
                    }}
                >
                    {saveKey}
                </pre>
            </ModalBody>
            <ModalFooter>
                <div
                    className='button modal-button'
                    onClick={toggle}
                >
                    Done
                </div>
            </ModalFooter>
        </Modal>
    );
};

export default SaveKeyModal;
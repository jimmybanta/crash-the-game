import {
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Tooltip
} from "reactstrap";

import React, { useState } from "react";

const CharactersModal = ({ toggle, characters, skillDescriptions }) => {
    // a modal that renders the game characters and their corresponding info
    // history, looks, personality, skills

    // if there was a problem retrieving the characters, display an error message
    const [displayError, setDisplayError] = useState((characters.length === 0));

    const initialCharacterState = characters.reduce((acc, character) => {
        acc[character.id] = false;
        return acc;
    }, {});
    // showCharacters is a dictionary that keeps track of whether a character's
    // info is shown or not
    const [showCharacters, setShowCharacters] = useState(initialCharacterState);

    const initialTooltipState = characters.reduce((acc, character) => {
        acc[character.id] = {};
        Object.keys(character.skills).forEach((skill) => {
            acc[character.id][skill] = false;
        });
        return acc;
    }, {});
    // tooltipOpen is a dictionary that keeps track of whether a given tooltip is open or not
    const [tooltipOpen, setTooltipOpen] = useState(initialTooltipState);

    const toggleTooltip = (characterId, skill) => {
        let tempTooltipOpen = { ...tooltipOpen };
        tempTooltipOpen[characterId][skill] = !tempTooltipOpen[characterId][skill];
        setTooltipOpen(tempTooltipOpen);
    };

    const renderCharacter = (character) => {
        // renders a character and their info
        const characterId = character.id;

        return (
            <div
                className="container flex-column"
                style={{
                    paddingTop: "20px",
                    paddingBottom: "20px",
                }}
            >
                <div
                    className="modal-text-header"
                    onClick={() => {
                        let tempShowCharacters = { ...showCharacters };
                        tempShowCharacters[characterId] = !tempShowCharacters[characterId];
                        setShowCharacters(tempShowCharacters);
                    }}
                >
                    {character.name}
                </div>

                {renderCharacterInfo(character)}
            </div>
        );
    };

    const renderCharacterInfo = (character) => {
        // renders a character's info
        const characterId = character.id;

        if (showCharacters[characterId]) {
            return (
                <div className="container flex-column" style={{}}>
                    <div className="modal-text-header-two">
                        <em>History</em>
                    </div>
                    <div className="modal-text">{character.history}</div>
                    <div className="modal-text-header-two">
                        <em>Looks</em>
                    </div>
                    <div className="modal-text">{character.physical_description}</div>
                    <div className="modal-text-header-two">
                        <em>Personality</em>
                    </div>
                    <div className="modal-text">{character.personality}</div>
                    <div className="modal-text-header-two">
                        <em>Skills</em>
                    </div>
                    <div className="modal-text">{renderSkills(character.id, character.skills)}</div>
                </div>
            );
        } else {
            return null;
        }
    };

    const renderSkills = (characterId, skills) => {
        // renders a character's skills
        let characterSkillDescriptions = {};

        skillDescriptions.forEach((skill) => {
            // capitalize each word in skill.name
            const tempName = skill.name
                .split(" ")
                .map((word) => {
                    return word.charAt(0).toUpperCase() + word.slice(1);
                })
                .join(" ");

            if (skill.name in skills) {
                characterSkillDescriptions[skill.name] = skill.description;
            } else if (tempName in skills) {
                characterSkillDescriptions[tempName] = skill.description;
            }
        });

        return (
            <div className="container flex-column">
                {Object.entries(skills).map(([skill, value]) => {
                    // create a unique id for the tooltip
                    const tooltipId = `${skill}-${characterId}`.replace(/ /g, "-");

                    return (
                        <div className="modal-text" key={skill}>
                            <strong id={tooltipId} className="modal-skill-text">
                                {skill}:
                            </strong>{" "}
                            &nbsp;
                            <Tooltip
                                placement="left"
                                isOpen={tooltipOpen[characterId][skill]}
                                toggle={() => toggleTooltip(characterId, skill)}
                                target={tooltipId}
                                type="dark"
                                effect="float"
                            >
                                {characterSkillDescriptions[skill]}
                            </Tooltip>
                            <em>{value}</em>
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <Modal centered size="lg" isOpen={true} toggle={toggle}>
            <ModalHeader>
                <div className="modal-text-header"
                style={{userSelect: 'none', cursor: 'default'}}>
                    Characters
                </div>
            </ModalHeader>
            <ModalBody style={{ maxHeight: "70vh", overflowY: "auto" }}>
                {displayError ? 
                <div className="modal-text">
                    There was a problem retrieving the characters.
                    </div> 
                    :
                    <div className="container flex-column" style={{ width: "100%", height: "100%" }}>
                    <div>
                        {characters.map((character) => {
                            return renderCharacter(character);
                        })}
                    </div>
                    <div className='modal-text'>
                        Click on a character's name to expand their info.
                    </div>
                    
                </div>
                    }
                
            </ModalBody>
            <ModalFooter>
                
                <div className="button modal-button" onClick={toggle}>
                    Done
                </div>
            </ModalFooter>
        </Modal>
    );
};

export default CharactersModal;

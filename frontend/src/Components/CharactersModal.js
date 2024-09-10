
import { 
    Modal, ModalHeader, 
    ModalBody, ModalFooter,
    Tooltip
} from "reactstrap";

import { React, useState } from "react";


const CharactersModal = ({ toggle, characters, skillDescriptions }) => {

    const initialCharacterState = characters.reduce((acc, character) => {
        acc[character.id] = false;
        return acc;
    }, {});

    const [showCharacters, setShowCharacters] = useState(initialCharacterState);

    const initialTooltipState = characters.reduce((acc, character) => {

        acc[character.id] = {};
        Object.keys(character.skills).forEach((skill) => {
            acc[character.id][skill] = false;
        });
        return acc;
    }, {});



    const [tooltipOpen, setTooltipOpen] = useState(initialTooltipState);





    const toggleTooltip = (characterId, skill) => {
        let tempTooltipOpen = {...tooltipOpen};
        tempTooltipOpen[characterId][skill] = !tempTooltipOpen[characterId][skill];
        setTooltipOpen(tempTooltipOpen);
    };

    



    const renderCharacter = (character) => {

        const characterId = character.id;
        
        return (
            <div className='container flex-column'
            style={{
                paddingTop: '20px', paddingBottom: '20px',
            }}>
                <div className='modal-text-header'
                
                onClick={(character) => {
                    let tempShowCharacters = {...showCharacters};
                    tempShowCharacters[characterId] = !tempShowCharacters[characterId];
                    setShowCharacters(tempShowCharacters);
                }}>
                    {character.name}
                </div>

                {renderCharacterInfo(character)}
            </div>
        );
    };

    const renderCharacterInfo = (character) => {

        const characterId = character.id;

        if (showCharacters[characterId]) {
            return (
                <div className='container flex-column'
                style={{}}>
                    <div className='modal-text-header-two'>
                        <em>History</em>
                    </div>
                    <div className='modal-text'>
                        {character.history}
                    </div>
                    <div className='modal-text-header-two'>
                        <em>Looks</em>
                    </div>
                    <div className='modal-text'>
                        {character.physical_description}
                    </div>
                    <div className='modal-text-header-two'>
                        <em>Personality</em>
                    </div>
                    <div className='modal-text'>
                        {character.personality}
                    </div>
                    <div className='modal-text-header-two'>
                        <em>Skills</em>
                    </div>
                    <div className='modal-text'>
                        {renderSkills(character.id, character.skills)}
                    </div>
                </div>
                
            );
        }
        else {
            return null;
        }
    }
    
    const renderSkills = (characterId, skills) => {

        let characterSkillDescriptions = {};

        skillDescriptions.forEach((skill) => {
            // capitalize each word in skill.name
            const tempName = skill.name.split(' ').map((word) => {
                return word.charAt(0).toUpperCase() + word.slice(1);
            }).join(' ');

            if (skill.name in skills) {
                characterSkillDescriptions[skill.name] = skill.description;
            }
            else if (tempName in skills) {
                characterSkillDescriptions[tempName] = skill.description;
            }
        });

        return (
            <div className='container flex-column'>

                {Object.entries(skills).map(([skill, value]) => {

                    const tooltipId = `${skill}-${characterId}`.replace(/ /g, '-');

                    return (
                        <div className='modal-text'
                        key={skill}>

                            <strong 
                                id={tooltipId}
                                className='modal-skill-text'>
                                {skill}: 
                            </strong> 
                            &nbsp;

                            <Tooltip
                            placement='left'
                            isOpen={tooltipOpen[characterId][skill]}
                            toggle={() => toggleTooltip(characterId, skill)}
                            target={tooltipId}
                            type='dark'
                            effect='float'
                            >
                                {characterSkillDescriptions[skill]}
                            </Tooltip>
                                <em>{value}</em>
                        </div>
                    );
                }
                )}
            </div>
        );
    }




    return (
    <Modal 
    centered
    size='lg'
    isOpen={true}
    toggle={toggle}>
        <ModalHeader 
        className='modal-text'
        style={{userSelect: 'none'}}>
            Characters -- click to expand
        </ModalHeader>
        <ModalBody style={{maxHeight: '70vh', overflowY: 'auto'}}>
            <div className='container flex-column'
            style={{width: '100%', height: '100%'}}>

                <div>
                    {characters.map((character) => {
                        return (
                            renderCharacter(character)
                        );
                    })}
                </div>
            </div>
            
        </ModalBody>
        <ModalFooter>
            <div className='button modal-button' 
                onClick={toggle}>Done</div>
        </ModalFooter>
    </Modal>
    );


};


export default CharactersModal;
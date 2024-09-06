import { React, useState } from 'react';

import { Button } from 'reactstrap';

import TextBox from '../Components/TextBox';

const text = "The snow swirls and drifts, obscuring the icy landscape. Samantha's eyes flutter open as she comes to, her head pounding. She coughs, the frigid air stinging her lungs. \n\n\"Where...where am I?\" she murmurs, disoriented. \n\nLiam is already on his feet, surveying the damage to the plane. \"Looks like we went down hard. That engine failure came out of nowhere.\"\n\nEsteban groans, pulling himself upright in his seat. \"This is...unacceptable. I demand to know how soon we can be rescued.\"\n\nSamantha takes in their surroundings, her brow furrowed. \"I don't think rescue is coming anytime soon. We're in the middle of nowhere.\"\n\nThe group falls silent as they gaze out at the vast, snow-covered expanse. In the distance, a shadowy shape can be seen, half-buried in the drifts.\n\n\"What is that?\" Esteban squints, peering through the blowing snow.\n\nLiam's expression grows grim. \"I don't know, but I have a feeling we're not alone out here.\"\n\nThe characters turn to face the mysterious structure, their breaths forming puffs of vapor in the frigid air. Samantha's eyes are alight with a gleam of scholarly curiosity, even as a hint of trepidation creeps into her voice.\n\n\"We need to investigate. There may be clues, or even a way to signal for help. But...I can't shake the feeling that we're not the first ones to stumble upon this place.\"\n\nThe player is left with a choice - what do they want the characters to do next? Venture out to explore the strange, half-buried structure, or stay put and try to secure the damaged plane? The path forward is uncertain, and the consequences of their actions could have profound implications.";

const Game = ({onSetCurrentPage}) => {


    return (
    <div className='container'
        style={{ display: 'flex', flexDirection: 'column', 
                justifyContent: 'flex-start', alignItems: 'top',
                height: '90%', width: '80%',
                textAlign: 'center', 
                border: '1px white solid',
        }}>
         
    </div>
    )
    }



export default Game;
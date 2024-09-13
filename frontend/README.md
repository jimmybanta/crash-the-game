# Crash - Frontend

The Crash frontend is written in HTML, CSS, and Javascript, 
with React as the framework.
It uses axios to make calls to the backend.

Responses from the LLM are streamed in using Server Sent Events (SSEs), from the backend.
Upon first render, a game will initiate a stream that is unique to that game ID.
It will continue to listen for updates from the backend until the page is exited.

## Main Pages
### Home
The landing page that a user sees when they first visit. Contains buttons that take you to the NewGame, LoadGame, and About pages.

### NewGame
A page where a player can setup a new game. 
It renders the Setup page. Then, when the setup configuration has been received from the Setup page, it passes the info to and renders the Game page, where the game will be played.

### Setup
A page where a player can choose a configuration for their game.
This includes choosing a theme, timeframe, and details.
Or, if they're so inclined, they can click 'setup for me', which will make a call to the backend to return a random configuration
(randomly selected from lists I've come up with).
Then, once they're happy with the configuration, they can click 'Let's Play!' to start the game.
This passes the configuration back to the NewGame page.

### LoadGame
A page where a player can load a game they've saved. They're prompted for their game save key, then they can hit 'Load Game'. 
It will make a call to the backend to check that the key is valid, and if it is, it will load the game info.
This game info will be passed to the Game page, where the game will be played.

### Game
The page where a game gets played. Handles different game situations - new game, loading game.
Displays the story's title in a header at the top, then displays all the text from the story,
and in a footer displays the place where the user can input their commands/choices, as well as buttons
to open up modals to show their characters and their corresponding skills, and to view their save key (so they can load the game later). 

### About
A page that gives a little bit of information about the game.
Displays the current version, which is retrieved from the backend.


## Components
### Header
A header that appears at the top of the Game page. Shows the title of the current story.

### Footer
A footer that appears at the bottom of the Game page. Contains the input box for the user to input their commands/choices, as well as buttons to open up modals to show their characters and their corresponding skills, and to view their save key (so they can load the game later).

### TextBox
A component that displays the text of the story. Using these, the full text of the story is split into these chunks. Each can be collapsed and expanded by clicking on them.

### Loading
Loading dots, with a corresponding animation. Used when we're waiting on the backend to return data.

### CharactersModal
A modal that displays the characters the player has in their party, as well as their corresponding information (like history, physical description, personality), and their skills.
Skills are listed, as well as the character's proficiency in each skill.
Each skill has a corresponding tooltip that opens up when hovered over, which displays the skill's description.

### SaveKeyModal
A modal that displays the player's save key. This key is used to load a game that the player has saved.

## utils/other files
### api.js
Contains the fuction used to make calls to the backend. Uses axios.

### BaseUrl.js
Contains the base URL for the backend. This is used in api.js to make calls to the backend.
Changes depending on the environment (development, staging, production).
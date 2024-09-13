# CRASH
Crash is an ai-generated, interactive story game.

It can be played at [crashthegame.com](https://crashthegame.com/).

A user can provide a theme, timeframe, and other details (or they can choose a random setup), and a story will be generated on the fly for them to play through and interact with.
A user is given a save key, which, as long as they hang on to it, will allow them to load their game later on and continue from where they left off.

At the beginning of a game, the backend generates a lot of information - it first returns a title for the story, based off the given game setup info.

Then, it returns a short story of a crash landing, setting the scene for the game.

While the user reads this first story, the backend generates a location name and description, for where their characters crash landed, as well as a set of skills that would be relevant in this location. Finally, it generates full character descriptions, including history, looks, personality, and their skill levels in the given skills.

Then, using all this information, the backend generates a story of the characters waking up after the crash landing in this new place, seeing their surroundings, meeting their fellow survivors.

Then, the backend returns a short intro blurb, introducing the user to the game, giving them some guidance on how to play.

Then the user is off and running - through a command line, they can essentially do whatever they want, and the backend will generate a response based on their input. 


## Design
### Backend
The backend (/backend) is built using Django.
It uses Server Sent Events to stream LLM responses to the frontend.

### LLM
The backend uses Anthropic's Claude family of models (haiku in particular) to generate text.
While a user plays the game, the backend automatically prompts the model to summarize the story and saves it to file, for prompting the LLM later - this is meant to decrease latency and save on costs - as a game gets longer and longer, prompting the LLM with the entire story can be slow.
It also uses Anthropic's prompt caching to a similar effect.

### Frontend
The frontend (/frontend) is built using React.

### Deployment
The application is deployed on AWS, using an ec2 instance to host the backend, and s3 + cloudfront to host the frontend.
The database is hosted on RDS, and the application is served using nginx and daphne.
Upon startup, the application pulls configuration from SSM parameter store.
All the game files are store in s3.
Route 53 is used to manage the domain and subdomains.
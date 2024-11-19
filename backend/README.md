# Crash Backend

The Crash backend is a Django application, that communicates to the frontend via a REST API as well as with Server Sent Events (SSEs).
It is essentially an LLM application, that uses Anthropic's Claude family of models (haiku in particular) to generate text.

## Games App
The games app contains all the game logic and code for the game. 

### Modules

#### apps.py
This module contains the configuration for the games app.

#### decorators.py
Contains decorators that are used for logging and retrying requests when they fail.

#### initialization.py
Contains various functions for initializing the game, by prompting the LLM for a title, location, characters, and skills.

#### load_game.py
Contains functions for loading a game from the database and file system.

#### model_prices.py
Contains a function for calculating the prices of LLM api calls.

#### models.py
Contains the models for the game.

#### prompting.py
Contains functions for calling the LLM.

#### s3.py
Contains functions for uploading and downloading files from S3.

#### save_game.py
Contains functions for saving the game to the database and file system.

#### serializers.py
Contains serializers for the game models.

#### summarize.py
Contains functions for calling the LLM to summarize chunks of text.

#### urls.py
Contains the urls for the game app.

#### utils.py
Contains utility functions for the game.

#### views.py
Contains the views for the game app.
This includes the main view that gets use - the main loop view. This runs whenever a user is playing a game, and inputs a command.
It creates the prompt for the LLM, sends it to the LLM, and then sends the response to the frontend via SSEs.


## Other files and folders
#### Assets
Contains text files for prompting and random setup of a game.
#### backend
Contains the settings for the Django application.
#### tests
Contains tests for the games app.
#### config.py
Contains the configuration for the game - runs on startup to pull values from s3 parameter store.
#### current_version.json
Contains the current version of the game.
#### manage.py
The Django management script.
#### requirements.txt
Contains the required python packages for the game.
#### version_log.txt
Contains the version history of the game.
# Unbelivaboat Cardcounter

A project aiming to card count in Unbelivaboat automatically and possibly play automatically. Unbelivaboat is an economy bot for discord. The black jack minigame is Card countable. This project aims to count the cards and then play the game optimally. Unbelivaboat plays the S17 variation of blackjack. This means that the dealer stands on a soft 17. And plays with three decks making card counting easier.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install the project, you can clone the repository and run the following command:

```bash
pip install -r requirements.txt
``` 

## Usage

Add the Betterdiscord plugin to your discord client. It will make the emotes of of discord larger and easier to read. This is important for the OCR to work effectively.

Then run the project. It will take a snipit of the discord window and then use OCR to read the cards. It will then count the cards and display the count.


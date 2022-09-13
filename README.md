# The Great Evolution Game
A Pygame project about AI, sociology and Darwin

> **Note**
>
> This readme is still a very draft, but here are some indications


## What is it?

The first goal of this project is to watch creatures dying.  
I mean, technically speaking, it's all squares having a very few brain cells to manage their health points, food points, their movements, and their interactions with other creatures.

I plan to add more and more interactions (both input and output neurons) in the simulation, but for now they can already do some very neat things. They're just too dumb for my great expectations I guess.


## Shortcuts

* `G` open cool charts in the bottom left
* `left arrow` and `right arrow` navigate between charts
* `P` put the game on pause (or resume)
* `left click` on a creature to open its details panel


## How to profile

First, install the required dependencies from `requirements-dev.txt`

Then use `py-spy top --subprocesses -- python3 start.py` if you want to get the live view of what functions are taking the most time,
or `py-spy record -o profile.svg --subprocesses -- python start.py` for a nice image at the end.

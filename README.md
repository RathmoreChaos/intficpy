# intficpy
A python library for writing parser-based interactive fiction. Currently in early development.

# Parser-based interactive fiction
Parser based interactive fiction, sometimes called text adventure, is a story displayed through text, that the reader/player interacts with by typing out commands. Typing "get lamp", for instance, will cause the character to take the lamp.

# Why intficpy?
Every other programming-based system for writing parser based interactive has its own language, useful only for writing interactive fiction. With intficpy, I wanted to make it possible for creators who already knew Python to use that knowledge for writing interactive fiction, and for creators new to Python to work in a language for which myriad tutorials, and a strong online community already exist.

# Development
My first and greatest challenge in building intficpy was writing the basic parser. Interacting with natural language commands is a complicated problem. In interactive fiction, the problem is much simplfied by the fact that every statement from the user is a direct order (imperative tense) and will always begin with a verb (or a direction). I made use of the pattern to quickly identify the main verb in every sentence, and determine the most probable syntax for the command. This approach proved very extensible once implemented.

I created the Thing class (with subclasses Surface, Container and Actor) to represent physical objects in the world of the story. I created the Verb class for verbs used in commands ("LOOK", "PUT shoe in box", etc). I created the Room class to refer to locations. 

At present, it is possible to develop a fully featured interactive fiction game in intficpy, but it will be easier to do so once intficpy is more fleshed out.

# Installation and Use
To install, download the intficpy folder, and place inside of a project folder. To use the GUI, you will need to have PyQt5 installed. Refer to test_game/testgame.py for terminal mode instructions. You will need to import the following files:

	# imports from other libraries
	import sys
	from PyQt5.QtWidgets import QApplication

	# imports from intficpy
	from intficpy.room import Room
	from intficpy.thing import Thing, Surface, Container, Clothing
	from intficpy.player import Player
	import intficpy.actor as actor
	import intficpy.parser as parser
	import intficpy.gui as gui

Currently, there are no instructions for creating games with IntFicPy. Feel free to experiment with testgame.py. To run it, place it in intficpy's parent folder, and run it with Python 3.

# License
IntFicPy is distributed with a GPL3 license
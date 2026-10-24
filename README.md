# text-adventure

A Text Adventure Game made in python, using only builtin libraries.
**This README is a WORK IN PROGRESS and will be improved later**

## How to play
This game is developed using python 3.15.1 earlier versions of python _might_ work but is not officially supported

To play download main.py and run

```bash
python main.py
```
Im assuming that if you are here you have python installed but if not download python [here](https://python.org/downloads/).

This game uses the python `cmd` library so using the up arrow will navigate to past commands entered. 
There is a built in help system type `?` or `help` for help on commands.
Any command that needs an name of an item or object will accept only part of the game as long as the substring entered only matches one thing in the room.
If you are playing from downloaded code on the main branch and not a release (or manually change the `DEBUG` flag to `True` in the code) starting any line with `!` will run that line as python code, though be carful there is no error handling. 


# EAA Assignment 3 Bonus 
implementation by Vladimir Vojnic Hajduk `11834787`

# How to run 
Python 3 needed (was implemented on 3.10.6 but that probably doesn't matter)

`python3 ./main.py`

# Adjust graph
One can adjust the number of verticies in the code.

A random graph gets generated from it. With the specified number of verticies
with each vertex having `0` to `delta` neighbouring verticies to it.

# Correctness
The random graph generation gets checked (that neighborhoods are 2 sided).

At the end the coloring correctness also gets checked (that the color is in the 
coloring range, and that no adjacent verticies have the same color)
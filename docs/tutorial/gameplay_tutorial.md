ver_0.3
controls:
- x,z (by default, may be changeble in later versions) to 'hit an object'
- mouse movement

objects:
circle:
- appears with an approach circle, which starts shrinking
- move your mouse over it and when it hits the outer edge of the circle, press 'x' or 'z' (by default) to hit it
- you gain score based on your timing

slider:
- appears as a circle with an approach circle and a path
- once the approach circle hits the outer edge of the circle, it starts moving along the path
- hold 'x' or 'z' while moving your mouse with the circle to sucessfully comlete it
- you gain more score based on the distance

gameplay:
- objects start appearing on your screen
- hit them to get score
- if you hit multiple in a row, you gain combo, which increases your score gain
- if you miss, you lose combo

hp:
- you lose hp if you miss an object
- you also lose hp passively for a few seconds if your combo remains at 0
- you gain hp when you gain score

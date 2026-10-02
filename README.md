Networked Battleship
A two-player Battleship game in Python using FLTK and TCP sockets.
Requirements: Python 3, pyfltk, and the four .png images in the same folder.
Run: Start the server first: python battleship.py server localhost 5000. Then start the client: python battleship.py client localhost 5000.
Each player places 5 ships, then takes turns guessing. The first to sink all 5 wins.

import PySimpleGUI as sg
import requests
import json
from flask import jsonify, Flask
from crypto import makePrivateKey

# Set theme https://pysimplegui.readthedocs.io/en/latest/#themes-automatic-coloring-of-your-windows
sg.theme('DarkBlack1')

# ------ Menu Definition ------ #
menu_def = [['&File', ['&Open', '&Save', '&Exit', 'Properties']],
            ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
            ['&Help', '&About...']]

# Layout for the objects inside the window
layout = [[sg.Menu(menu_def, tearoff=True)],
          [sg.Button('Mine a block')],
          [sg.Button('Download Current Chain')],
          [sg.Button('Generate a new key')],
          [sg.Text('No current key', key='walletText')],
          [sg.Button('Close')]
          ]

# Initialize window with title, our layout defined above, and a size
window = sg.Window('Mining Client', layout, size=(600, 400))

# Hard coded URLs til the client launches the Daemon
# Eventually these will be automatically set
miningURL = 'http://192.168.0.9:5000/mine'
chainURL = 'http://192.168.0.9:5000/chain'


# ----- Function Definitions ----- #
# Mine a new block via the mining url
def mineBlock():
    r = requests.post(miningURL)
    print("Mining successful")


# Save our current chain to a local text file
def saveChain():
    c = requests.get(chainURL)
    print(c.text)
    with open('chain.txt', 'w') as outfile:
        outfile.write(c.text)


# Basic functionality for generating a new private key
def makeKey():
    newKey = makePrivateKey()
    newKey = newKey.to_string().hex()
    window['walletText'].update(newKey)
    with open('keys.txt', 'a') as outfile:
        outfile.write(newKey)
        outfile.write('\n')


# TODO Start/stop daemon with client
# TODO Start/stop continual mining
# TODO Store IPs of current connections
# TODO Attempt to reconnect to previous connections upon startup, removing if necessary
# TODO Safely store local keys
# TODO Allow user to select between locally stored private keys
# TODO Basic transaction screen
# TODO Wallet balance screen


# While loop to continually check for events within the window
# Perform relevant actions when necessary
# Might have to thread things eventually so client doesn't lock up when performing a long task
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Close':
        break
    elif event == 'Mine a block':
        mineBlock()
    elif event == 'Download Current Chain':
        saveChain()
    elif event == 'Generate a new key':
        makeKey()

window.close()

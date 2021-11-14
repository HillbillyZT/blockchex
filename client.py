import PySimpleGUI as sg
import requests
import json
from crypto import makePrivateKey
import keyring
import webbrowser


# Find first private key stored in keys.txt before defining our menu
# This lets us populate the field on declaration
with open('keys.txt', 'r') as outfile:
    currentWallet = outfile.readline()

# Set theme https://pysimplegui.readthedocs.io/en/latest/#themes-automatic-coloring-of-your-windows
sg.theme('DarkBlack1')

# ------ Menu Definition ------ #
menu_def = [['&Wallet', ['&View', '&Import', '&Export', 'Properties']],
            ['&View', ['Block', ['By Height', 'By Hash', ], 'Chain'], ],
            ['&Help', '&About...']]

# ----- Layout Definition ----- #
# Layout for the objects inside the window
# Key value allows us to update/use variable by reference
layout = [[sg.Menu(menu_def, tearoff=False)],
          [sg.Button('Mine a block')],
          [sg.Button('Download Current Chain')],
          [sg.InputText(key='blockHeightInput'), sg.Button('Lookup block by height')],
          [sg.InputText(key='blockHashInput'), sg.Button('Lookup block by hash')],
          [sg.Button('Generate a new key')],
          [sg.Text('Wallet: ' + currentWallet, key='walletText')],
          [sg.Button('Close')]
          ]

# Most of these are goals that will not be addressed within the scope of this semester
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
def runClient(serverURL: str):
    # Initialize window with title, our layout defined above, and a size
    window = sg.Window('Mining Client', layout, size=(600, 400))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Close':
            break
        elif event == 'Mine a block':
            mineBlock(serverURL)
        elif event == 'Download Current Chain':
            saveChain(serverURL)
        elif event == 'Generate a new key':
            makeKey(window)
        elif event == "Lookup block by height":
            blockHeightResult = lookupBlockHeight(serverURL, values['blockHeightInput'])
            sg.popup(blockHeightResult, keep_on_top=True)
        elif event == "Lookup block by hash":
            blockHashResult = lookupBlockHash(serverURL, values['blockHashInput'])
            sg.popup(blockHashResult, keep_on_top=True)
        elif event == "About...":
            webbrowser.open('https://github.com/HillbillyZT/blockchex#readme')

    window.close()


# ----- Function Definitions ----- #
# These functions get called within our window loop
# Perform relevant actions based on function + variable input

# Mine a new block via the mining url
def mineBlock(serverURL):
    miningURL = serverURL + '/mine'
    r = requests.post(miningURL)
    print("Mining successful")


# Save our current chain to a local text file
def saveChain(serverURL):
    chainURL = serverURL + '/chain'
    c = requests.get(chainURL)
    data = c.json()
    print(c.text)
    with open('chain.txt', 'w') as outfile:
        outfile.write(json.dumps(data))


# Basic functionality for generating a new private key
def makeKey(window):
    newKey = makePrivateKey()
    newKey = newKey.to_string().hex()
    window['walletText'].update(newKey)
    with open('keys.txt', 'a') as outfile:
        outfile.write(newKey)
        outfile.write('\n')


# Take height from user and use a get request to return the info
def lookupBlockHeight(serverURL, height: int):
    heightURL = serverURL + '/blockHeight/' + str(height)
    b = requests.get(heightURL)
    with open('block.txt', 'w') as outfile:
        outfile.write(str(b.text))
    return str(b.text)


# Take hash from user and use a get request to return the info
def lookupBlockHash(serverURL, hash: int):
    hashURL = serverURL + '/blockHash/' + str(hash)
    b = requests.get(hashURL)
    with open('block.txt', 'w') as outfile:
        outfile.write(str(b.text))
    return str(b.text)

from blockchain import Blockchain
import blockchain
import PySimpleGUI as sg
import requests
import json
import pyperclip
import wallet
from crypto import makePrivateKey
import keyring
import webbrowser


# Find first private key stored in keys.txt before defining our menu
# This lets us populate the field on declaration
# TODO Check if this file exists first
with open('keys.txt', 'r') as outfile:
    currentWallet = outfile.readline()

# Set theme https://pysimplegui.readthedocs.io/en/latest/#themes-automatic-coloring-of-your-windows
sg.theme('DarkBlack1')

# ------ Menu Definition ------ #
menu_def = [['&Wallet', ['&View', '&Import', '&Export', 'Properties']],
            ['&View', ['Block', ['By Height', 'By Hash', ], 'Chain'], ],
            ['&Help', '&About']]

# ----- Layout Definition ----- #
# Layout for the objects inside the window
# Key value allows us to update/use variable by reference
layout = [[sg.Menu(menu_def, tearoff=False)],
          [sg.Button('Mine a block', key='mineBlock')],
          [sg.Button('Download Current Chain', key='download')],
          [sg.Button('Send Crypto', key='txPopup')],
          [sg.InputText(key='blockHeightInput'), sg.Button('Lookup block by height', key='lookupHeight')],
          [sg.InputText(key='blockHashInput'), sg.Button('Lookup block by hash', key='lookupHash')],
          [sg.Button('Generate a new key', key='keyGen')],
          [sg.Text('Wallet: ' + currentWallet, key='walletText')],
          [sg.Button('Copy Wallet Address', key='copyWallet')],
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


def txPopup():
    layout = [
        [sg.Text('Send to: '), sg.InputText(key='peer_address')],
        [sg.Text('Amount: '), sg.InputText(key='amount')],
        [sg.Button('Submit', key='txSubmit')]
    ]
    window = sg.Window("Create Transaction", layout, use_default_focus=False, finalize=True, modal=True)
    event, values = window.read()
    window.close()
    return values


# While loop to continually check for events within the window
# Perform relevant actions when necessary
# Might have to thread things eventually so client doesn't lock up when performing a long task
def runClient(serverURL: str):
    # Initialize window with title, our layout defined above, and a size
    window = sg.Window('Mining Client', layout, size=(600, 400), finalize=True)

    with open('keys.txt', 'r') as outfile:
        currentWallet = outfile.readline()
    
    
    while True:
        event, values = window.read()
        window['walletText'].update(currentWallet)
        if event == sg.WIN_CLOSED or event == 'Close':
            saveChain(serverURL)
            break
        elif event == 'mineBlock':
            mineBlock(serverURL)
        elif event == 'download':
            saveChain(serverURL)
        elif event == 'txPopup':
            txValues = txPopup()
            print(txValues['peer_address'], txValues['amount'])
            # TODO Pass unspentTxOuts to build_tx below
            blockchain.generate_next_block_with_transaction(str(txValues['peer_address']), float(txValues['amount']))
            #wallet.build_tx(str(txValues['peer_address']), float(txValues['amount']), wallet.get_private_key_from_string(currentWallet), blockchain.unspentTxOuts)
        elif event == 'keyGen':
            makeKey(window)
        elif event == "lookupHeight":
            blockHeightResult = lookupBlockHeight(serverURL, values['blockHeightInput'])
            sg.popup(blockHeightResult, keep_on_top=True)
        elif event == "lookupHash":
            blockHashResult = lookupBlockHash(serverURL, values['blockHashInput'])
            sg.popup(blockHashResult, keep_on_top=True)
        elif event == 'copyWallet':
            pyperclip.copy(currentWallet)
        elif event == "About":
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
    newKeyText = 'Wallet: ' + newKey
    window['walletText'].update(newKeyText)
    with open('keys.txt', 'a') as outfile:
        outfile.write(newKey)
        outfile.write('\n')


# Take height from user and use a get request to return the info
def lookupBlockHeight(serverURL, height: int):
    heightURL = serverURL + '/blockHeight/' + str(height)
    b = requests.get(heightURL)
    # with open('block.txt', 'w') as outfile:
    #     outfile.write(str(b.text))
    return str(b.text)


# Take hash from user and use a get request to return the info
def lookupBlockHash(serverURL, hash: int):
    hashURL = serverURL + '/blockHash/' + str(hash)
    b = requests.get(hashURL)
    # with open('block.txt', 'w') as outfile:
    #     outfile.write(str(b.text))
    return str(b.text)

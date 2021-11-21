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

KILL_PROCESS: bool = False

# Set theme https://pysimplegui.readthedocs.io/en/latest/#themes-automatic-coloring-of-your-windows
sg.theme('DarkBlack1')

# ------ Menu Definition ------ #
menu_def = [['&Wallet', ['&View Balance', '&Copy Address']],
            ['&View', ['Block', ['By Height', 'By Hash', ], 'Chain'], ],
            ['&Network', ['View Connections', 'New Connection'], ],
            ['&Help', '&About']]

# ----- Layout Definition ----- #
# Layout for the objects inside the window
# Key value allows us to update/use variable by reference
layout = [[sg.Menu(menu_def, tearoff=False)],
          [sg.Button('Mine a block', key='mineBlock')],
          [sg.Button('Download Current Chain', key='download')],
          [sg.Button('Send Crypto', key='txPopup')],
          #[sg.InputText(key='blockHeightInput'), sg.Button('Lookup block by height', key='lookupHeight')],
          #[sg.InputText(key='blockHashInput'), sg.Button('Lookup block by hash', key='lookupHash')],
          #[sg.Button('Generate a new key', key='keyGen')],
          [sg.Text('Wallet: ', key='walletText')],
          #[sg.Button('Copy Wallet Address', key='copyWallet')],
          #[sg.Button('Display balance', key='displayBalance')],
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


def heightPopup():
    layout = [
        [sg.Text('Block Height: '), sg.InputText(key='blockHeight')],
        [sg.Button('Submit')]
    ]
    window = sg.Window("Input Height", layout, use_default_focus=False, finalize=True)
    event, values = window.read()
    window.close()
    return values


def hashPopup():
    layout = [
        [sg.Text('Block Hash: '), sg.InputText(key='blockHash')],
        [sg.Button('Submit')]
    ]
    window = sg.Window("Input Hash", layout, use_default_focus=False, finalize=True)
    event, values = window.read()
    window.close()
    return values


def connectionPopup():
    layout = [
        [sg.Text('IP Address: '), sg.InputText(key='newConnection')],
        [sg.Button('Submit')]
    ]
    window = sg.Window("Input Peer IP Address", layout, use_default_focus=False, finalize=True)
    event, values = window.read()
    window.close()
    return values


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
    window = sg.Window('Mining Client', layout, size=(800, 400), finalize=True)

    pubkey = wallet.get_public_key_from_wallet().to_string().hex()
    currentWallet = "Wallet: " + pubkey

    while True:
        event, values = window.read(timeout=10)
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
            if txValues is not None:
                blockchain.generate_next_block_with_transaction(str(txValues['peer_address']), float(txValues['amount']))
        # elif event == 'keyGen':
        #     makeKey(window)
        elif event == "By Height":
            heightNum = heightPopup()
            if heightNum is not None:
                blockHeightResult = lookupBlockHeight(serverURL, heightNum['blockHeight'])
                sg.popup(blockHeightResult, keep_on_top=True)
        elif event == "By Hash":
            hashInput = hashPopup()
            if hashInput is not None:
                blockHashResult = lookupBlockHash(serverURL, hashInput['blockHash'])
                sg.popup(blockHashResult, keep_on_top=True)
        elif event == "Copy Address":
            pyperclip.copy(pubkey)
        elif event == "View Balance":
            balance = "Balance: " + displayBalance(serverURL)
            sg.popup(balance, keep_on_top=True)
        elif event == "Chain":
            chain = viewChain(serverURL)
            #sg.popup(chain, keep_on_top=True).Layout()
            #chainPopup(chain)
        elif event == "New Connection":
            newAddress = connectionPopup()
            if newAddress is not None:
                #Send address to /newpeer
                createConnection(serverURL, newAddress["newConnection"])
        elif event == "View Connections":
            activeConnections = viewConnections(serverURL)
            sg.popup(activeConnections, keep_on_top=True)
        elif event == "About":
            webbrowser.open('https://github.com/HillbillyZT/blockchex#readme')

    window.close()
    global KILL_PROCESS
    KILL_PROCESS = True

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


def displayBalance(serverURL):
    balanceURL = serverURL + '/getBalance'
    b = requests.get(balanceURL)
    bal = float(b.text)
    bal_prec = f"{bal:.3f}"
    return str(bal_prec)


def viewChain(serverURL):
    chainURL = serverURL + '/chain'
    b = requests.get(chainURL)
    return str(b.text)


def createConnection(serverURL, newAddress):
    connectionURL = newAddress + ":5000"
    postURL = serverURL + '/newPeer'
    b = requests.post(postURL, data=connectionURL)
    return


def viewConnections(serverURL):
    connectionURL = serverURL + '/getPeers'
    b = requests.get(connectionURL)
    return str(b.text)

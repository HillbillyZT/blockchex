import tkinter as tk
from tkinter.ttk import *
import PySimpleGUI as sg
import requests
# import webbrowser
import json
from flask import jsonify, Flask
from crypto import makePrivateKey

sg.theme('DarkBlack1')

# ------ Menu Definition ------ #
menu_def = [['&File', ['&Open', '&Save', '&Exit', 'Properties']],
            ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
            ['&Help', '&About...']]

layout = [[sg.Menu(menu_def, tearoff=True)],
          [sg.Button('Mine a block')],
          [sg.Button('Download Current Chain')],
          [sg.Button('Generate a new key')],
          [sg.Text('No current key', key='walletText')],
          [sg.Button('Close')]
          ]

window = sg.Window('Mining Client', layout, size=(600, 400))

miningURL = 'http://192.168.0.9:5000/mine'
chainURL = 'http://192.168.0.9:5000/chain'


def mineBlock():
    r = requests.post(miningURL)
    print("Mining successful")


def saveChain():
    c = requests.get(chainURL)
    print(c.text)
    with open('chain.txt', 'w') as outfile:
        outfile.write(c.text)
    # webbrowser.open(chainURL)


def makeKey():
    newKey = makePrivateKey()
    newKey = newKey.to_string().hex()
    window['walletText'].update(newKey)
    with open('keys.txt', 'a') as outfile:
        outfile.write(newKey)
        outfile.write('\n')


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

import tkinter as tk
import requests
#import webbrowser
import json
from flask import jsonify

window = tk.Tk(className='mining client')
window.geometry("450x200")

miningURL='http://192.168.0.9:5000/mine'
chainURL='http://192.168.0.9:5000/chain'

def mineBlock():
    r = requests.post(miningURL)
    print("Mining successful")

def viewChain():
    c = requests.get(chainURL)
    with open('chain.txt', 'w') as outfile:
        outfile.write(c.text)
    #webbrowser.open(chainURL)

miningButton = tk.Button(text="Mine a block", command=mineBlock)
viewingButton = tk.Button(text="View current chain", command=viewChain)
miningButton.pack()
viewingButton.pack()

window.mainloop()
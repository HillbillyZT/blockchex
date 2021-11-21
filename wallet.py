from ecdsa.keys import SigningKey, VerifyingKey
from crypto import TxIn, UnspentTxOut, TxOut, Transaction, getTransactionId, signTxIn
import crypto
from os.path import exists


# Get from file
def get_private_key_from_wallet() -> SigningKey:
    # Temporarily gonna just use a default
    with open('keys.txt', 'r') as outfile:
        privateKey = outfile.readline()
        keyobj = SigningKey.from_string(bytes.fromhex(privateKey))
        return keyobj


# Not actually from file
def get_public_key_from_wallet() -> VerifyingKey:
    private_key: SigningKey = get_private_key_from_wallet()
    public_key: VerifyingKey = private_key.get_verifying_key()
    return public_key


def get_private_key_from_string(key: str) -> SigningKey:
    return SigningKey.from_string(bytearray.fromhex(key))

def generate_new_private_key() -> SigningKey:
    key = SigningKey.generate()
    return key


# Checks for the existence of a key file first
# If no key file exists, make a key, add to file.
# If a key file exists, exit. The functions above
# will use it.
def init_wallet() -> None:
    # Check for existing key file
    if exists('keys.txt'):
        return
    else:
        newKey = crypto.makePrivateKey()
        newKey = newKey.to_string().hex()
        with open('keys.txt', 'a') as outfile:
            outfile.write(newKey)


def get_balance(address: str, unspentTxOuts: list[UnspentTxOut]) -> float:
    ourTxO: list[UnspentTxOut] = []
    for utxo in unspentTxOuts:
        if utxo._address == address:
            ourTxO.append(utxo)
    
    sum = 0
    for utxo in ourTxO:
        sum += utxo._amount
    
    return sum


def find_required_txouts(amount: float, ourUnspentTxOuts: list[UnspentTxOut]) -> tuple[list[UnspentTxOut], float]:
    # Algorithm from NaiveCoin:
    current_amount: float = 0
    inclUTxO: list[UnspentTxOut] = []
    
    for utxo in ourUnspentTxOuts:
        inclUTxO.append(utxo)
        current_amount += utxo._amount
        if current_amount >= amount:
            leftover = current_amount - amount
            return (inclUTxO, leftover)
    
    # If we get here, we did not have enough money to make the TX
    return (False, False)


# Make sure that we spent the total of the TxOut, sending the extra coins back to ourselves
def build_txouts(peer_address: str, my_address: str, amount: float, leftover: float):
    txout: TxOut = TxOut(peer_address, float(amount))
    if leftover == 0:
        return [txout]
    else:
        leftoverTxO: TxOut = TxOut(my_address, leftover)
        return [txout, leftoverTxO]


def build_tx(peer_address: str, amount: float, private_key: SigningKey, unspentTxOuts: list[UnspentTxOut]) -> Transaction:
    my_public_key: VerifyingKey = private_key.verifying_key
    my_address = my_public_key.to_string().hex()
    my_utxos: list[UnspentTxOut] = list(filter(lambda utxo: utxo._address == my_address, unspentTxOuts))
    
    incl_utxo, leftover = find_required_txouts(amount, my_utxos)
    if isinstance(incl_utxo, bool):
        print("INSUFFICIENT FUNDS")
        return False
    
    # Try this instead of lambda?
    def to_txin(utxo: UnspentTxOut):
        txin: TxIn = TxIn(utxo._txOutId, utxo._txOutIndex, "")
        return txin
    
    # For each of our utxos we need to turn it into a txin
    unsigned_tx_ins: list[TxIn] = list(map(to_txin, incl_utxo))
    
    tx: Transaction = Transaction()
    tx.txIns = unsigned_tx_ins
    tx.txOuts = build_txouts(peer_address, my_address, amount, leftover)
    tx.id = getTransactionId(tx)
    
    # Sign each TxIn
    def signall(txin: TxIn, index):
        txin.signature = signTxIn(tx, index, private_key.to_string().hex(), unspentTxOuts)
        return txin
    
    tx.txIns = [signall(b, a) for (a,b) in enumerate(tx.txIns)]
        
    # tx.txIns = list(map(signall, enumerate(tx.txIns)[0], enumerate(tx.txIns)[1]))
    
    return tx
    
# Testing
sk = SigningKey.generate()
pk: VerifyingKey = sk.get_verifying_key()

print(sk.to_string().hex())
print(pk.to_string().hex())
    
    
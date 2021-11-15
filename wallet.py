from ecdsa.keys import SigningKey, VerifyingKey
from crypto import TxIn, UnspentTxOut, TxOut, Transaction, getTransactionId, signTxIn
import crypto

# Get from file
def get_private_key_from_wallet() -> SigningKey:
    pass

# Not actually from file
def get_public_key_from_wallet() -> VerifyingKey:
    private_key = get_private_key_from_wallet()
    public_key = private_key.get_verifying_key()
    return public_key

def generate_new_private_key() -> SigningKey:
    key = SigningKey.generate()
    return key


# The stuff Bailey did in client should move here !!!
def init_wallet() -> None:
    # Check for existing key file
    # if (existsKey):
    #   return;
    # else:
    #   writeFile(key)
    pass


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
    current_amount = 0
    inclUTxO: list[UnspentTxOut] = []
    
    for utxo in ourUnspentTxOuts:
        current_amount += utxo._amount
        if current_amount >= amount:
            leftover = current_amount - amount
            return (inclUTxO, leftover)
    
    # If we get here, we did not have enough money to make the TX
    return (False, False)

# Make sure that we spent the total of the TxOut, sending the extra coins back to ourselves
def build_txouts(peer_address: str, my_address: str, amount: float, leftover: float):
    txout: TxOut = TxOut(peer_address, amount)
    if leftover == 0:
        return [txout]
    else:
        leftoverTxO: TxOut = TxOut(my_address, leftover)
        return [txout, leftoverTxO]


def build_tx(peer_address: str, amount: float, private_key: SigningKey, unspentTxOuts: list[UnspentTxOut]) -> Transaction:
    my_public_key: VerifyingKey = private_key.verifying_key
    my_address = my_public_key.to_string()
    my_utxos: list[UnspentTxOut] = filter(lambda utxo: utxo._address == my_address, unspentTxOuts)
    
    incl_utxo, leftover = find_required_txouts(amount, my_utxos)
    
    # Try this instead of lambda?
    def to_txin(utxo: UnspentTxOut):
        txin: TxIn = TxIn(utxo._txOutId, utxo._txOutIndex, "")
        return txin
    
    # For each of our utxos we need to turn it into a txin
    unsigned_tx_ins: list[TxIn] = map(to_txin, incl_utxo)
    
    tx: Transaction = Transaction()
    tx.txIns = unsigned_tx_ins
    tx.txOuts = build_txouts(peer_address, my_address, amount, leftover)
    tx.id = getTransactionId(tx)
    
    # Sign each TxIn
    def signall(txin: TxIn, index):
        txin.signature = signTxIn(tx, index, private_key.to_string(), unspentTxOuts)
        return txin
    tx.txIns = map(signall, tx.txIns)
    
    
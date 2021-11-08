from ecdsa import SigningKey
from hashlib import sha256
from functools import reduce

from ecdsa.keys import VerifyingKey


# Transaction outputs
class TxOut:
    def __init__(self, address: str, amount: float) -> None:
        self.address = address
        self.amount = amount


# Transaction inputs
class TxIn:
    def __init__(self, outId: str, outIndex: int, signature: str) -> None:
        self.outId = outId
        self.outIndex = outIndex
        self.signature = signature


# Transaction class containing lists of all txs in and out
class Transaction:
    def __init__(self, id: str = "", txIns: list[TxIn] = [], txOuts: list[TxOut] = []) -> None:
        self.id = id
        self.txIns = txIns
        self.txOuts = txOuts


# We will collect all of the relevant unspent outputs as these
class UnspentTxOut:
    def __init__(self, txOutId: str, txOutIndex: int, address: str, amount: float) -> None:
        self._txOutId = txOutId
        self._txOutIndex = txOutIndex
        self._address = address
        self._amount = amount


# Lambdas for days
# TODO Chris pls explain this
def getTransactionId(tx: Transaction) -> str:
    txInsStr: str = reduce(lambda x, y: x + y, map(lambda a: str(a.outId) + str(a.outIndex), tx.txIns))
    txOutStr: str = reduce(lambda x, y: x + y, map(lambda a: str(a.address) + str(a.amount), tx.txOuts))
    unencoded: str = txInsStr + txOutStr
    hash = sha256(unencoded.encode()).hexdigest()
    return hash


# TODO Find our unspent outputs; tokens we currently have to spend ?
def findUnspentTxOut(txId: str, index: int, unspentTxOuts: list[UnspentTxOut]) -> TxOut:
    return next(filter(lambda utxo: utxo._txOutId == txId and utxo._txOutIndex == index, unspentTxOuts))


# Generate a signing key and return it
def makePrivateKey() -> SigningKey:
    return SigningKey.generate()


# Use our private key to view our public key
def getPublicKey(privateKey: str) -> str:
    return SigningKey.from_string(privateKey).verifying_key


# TODO method to allow users to input private key for access/verification
def checkPrivateKey(privateKey: str) -> str:
    # If valid input return true
    return True
    # Else return false


# TODO Chris explain pls
def signTxIn(tx: Transaction, txInIndex: int, privateKey: str, unspentTxOuts: list[UnspentTxOut]) -> str:
    txIn = tx.txIns[txInIndex]
    payload = tx.id
    unspentTxOut = findUnspentTxOut(txIn.outId, txIn.outIndex, unspentTxOuts)

    # Attempted to sign invalid txout
    if not unspentTxOut:
        print("This shouldn't happen...")
        raise Exception('could not find referenced output')

    address = unspentTxOut.address

    if (getPublicKey(privateKey) != address):
        print("Signing key does not match Verifying key.")
        raise Exception('invalidKey')

    truePrivateKey = SigningKey.from_string(privateKey)

    signature: bytes = truePrivateKey.sign(payload.encode())
    return signature.hex()


# This function is nasty as hell
def updateUnspent(newTransactions: list[Transaction], unspentTxOuts: list[UnspentTxOut]) -> list[UnspentTxOut]:
    # Get all of the txOuts of new transactions, merge into one list
    unspentTxOuts_additional: list[UnspentTxOut]
    # This may need to be reduced
    unspentTxOuts_additional = list(map(lambda tx: \
        map(lambda txout, idx: UnspentTxOut(tx.id, idx, txout.address, txout.amount), tx.txOuts), \
        enumerate(newTransactions)))
    
    # Reduced:
    unspentTxOuts_additional = sum(unspentTxOuts_additional, [])
    
    # Get all of the txIns of new transactions, merge into one list
    spentTxOuts: list[UnspentTxOut] = list(map(lambda x: x.txIns, newTransactions))
    spentTxOuts = sum(spentTxOuts, [])
    spentTxOuts = list(map(lambda txin: UnspentTxOut(txin._txOutId, txin._txOutIndex, '', 0), spentTxOuts))
    
    # Determine full set of unspent txouts by adding new txouts and removing spent ones
    newUnspentTxOuts: list[UnspentTxOut] = list(filter(lambda utxo: \
        not findUnspentTxOut(utxo._txOutId, utxo._txOutIndex, spentTxOuts),unspentTxOuts))
        
    newUnspentTxOuts.extend(unspentTxOuts_additional)
    
    return newUnspentTxOuts
    

# Yeah this can be done later its boring
# TODO(Chris) this shit
def isValidTransactionStructure(tx: Transaction) -> bool:
    pass


# Validate a TxIn
def validateTxIn(txin: TxIn, tx: Transaction, unspentTxOuts: list[UnspentTxOut]) -> bool:
    referencedUTxO: UnspentTxOut
    referencedUTxO = next(filter(lambda utxo: \
        utxo._txOutId == txin.outId, unspentTxOuts))
    
    if not referencedUTxO:
        print("Referenced TxOut not found among specified UnspentTxOuts.")
        return False
    
    address = referencedUTxO._address
    
    verifying_key = VerifyingKey.from_string(address)
    return verifying_key.verify(txin.signature, tx.id)


def getTxInAmount(txIn: TxIn, unspentTxOuts: list[UnspentTxOut]) -> float:
    return findUnspentTxOut(txIn.outId, txIn.outIndex, unspentTxOuts).amount


# Validate a full Transaction
def validateTransaction(tx: Transaction, unspentTxOuts: list[UnspentTxOut]) -> bool:
    if(getTransactionId(tx) != tx.id):
        print('Invalid transaction ID: ' + str(tx.id))
        return False
    
    # Validate all Transaction's TxIns
    hasAllValidTxIns: bool = reduce(lambda x, y: x and y, \
        map(lambda txin: validateTxIn(txin, tx, unspentTxOuts), tx.txIns))
    
    if not hasAllValidTxIns:
        print("One or more of the Transaction's TxIns are invalid.")
        return False
    
    # Sum input and output amounts; can't send more than we spend
    sumTxInValues: float = reduce(lambda x,y: x + y,  \
        map(lambda txin: getTxInAmount(txin, unspentTxOuts),tx.txIns))
    
    sumTxOutValues: float = reduce(lambda x,y: x + y, \
        map(lambda txout: txout.amount, tx.txOuts))
    
    if sumTxInValues != sumTxOutValues:
        print("Transaction input amounts do not match transaction output amounts.")
        return False
    
    # Done :D
    return True



# ----- Testing ----- #

# private_key = SigningKey.generate()
# public_key = private_key.verifying_key
# data = "temst"

# signature: bytes = private_key.sign(data.encode())
# print("Signature: " + str(signature.hex()))

# print("Signature verifies: " + str(public_key.verify(signature, data.encode())))

# print("A few different ways to output keys: ")
# print(private_key.to_string().hex())
# print()
# print(private_key.to_pem().decode())
# print()
# print(private_key.to_der().hex())

# t_txin1 = TxIn("outID1", "outIndex1", "signature1")
# t_txin2 = TxIn("outID2", "outIndex2", "signature2")

# t_txout1 = TxOut("address1", "amount1")
# t_txout2 = TxOut("address2", "amount2")

# t_tx = Transaction("", [t_txin1, t_txin2], [t_txout1, t_txout2])

# print(getTransactionId(t_tx))

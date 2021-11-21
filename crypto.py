from ecdsa import SigningKey
from hashlib import sha256
from functools import reduce

from ecdsa.keys import VerifyingKey


# Easy number to do math with :D
COINBASE_PAYOUT: float = 10.0

# Transaction outputs
class TxOut:
    def __init__(self, address: str, amount: float) -> None:
        self.address = address
        self.amount = amount
    
    def __str__(self) -> str:
        return str(self.address) + str(self.amount)
    
    def __repr__(self):
        return str(self)


# Transaction inputs
class TxIn:
    def __init__(self, outId: str, outIndex: int, signature: str) -> None:
        self.outId = outId
        self.outIndex = outIndex
        self.signature = signature
    
    def __str__(self) -> str:
        return str(self.outId) + str(self.outIndex) + str(self.signature)
    
    def __repr__(self):
        return str(self)


# Transaction class containing lists of all txs in and out
class Transaction:
    def __init__(self, id: str = "", txIns: list[TxIn] = [], txOuts: list[TxOut] = []) -> None:
        self.id = id
        self.txIns = txIns
        self.txOuts = txOuts
    
    def __str__(self) -> str:
        return str(self.id) + str(self.txIns) + str(self.txOuts)
    
    def __repr__(self):
        return str(self)
    
    def to_dict(u):
        if isinstance(u, Transaction):
            mydict = {
                "id": u.id,
                "txIns": u.txIns.__dict__,
                "txOuts": u.txOuts
            }
            return mydict
        else:
            print("cry")


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
def findUnspentTxOut(txId: str, index: int, unspentTxOuts: list[UnspentTxOut]) -> UnspentTxOut:
    for utxo in unspentTxOuts:
        if utxo._txOutId == txId and utxo._txOutIndex == index:
            return utxo
    # return next(filter(lambda utxo: utxo._txOutId == txId and utxo._txOutIndex == index, unspentTxOuts))


# Generate a signing key and return it
def makePrivateKey() -> SigningKey:
    return SigningKey.generate()


# Use our private key to view our public key
def getPublicKey(privateKey: str) -> str:
    return SigningKey.from_string(bytearray.fromhex(privateKey)).verifying_key


# TODO method to allow users to input private key for access/verification
def checkPrivateKey(privateKey: str) -> bool:
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

    address = unspentTxOut._address

    if (getPublicKey(privateKey).to_string().hex() != address):
        print("Signing key does not match Verifying key.")
        raise Exception('invalidKey')

    truePrivateKey = SigningKey.from_string(bytearray.fromhex(privateKey))

    signature: bytes = truePrivateKey.sign(payload.encode())
    return signature.hex()


# This function is nasty as hell
def updateUnspent(newTransactions: list[Transaction], unspentTxOuts: list[UnspentTxOut]) -> list[UnspentTxOut]:
    # Get all of the txOuts of new transactions, merge into one list
    unspentTxOuts_additional: list[UnspentTxOut]
    # This may need to be reduced
    
    def local_build_txout(var, tx):
        (txout, idx) = var
        return UnspentTxOut(tx.id, idx, txout.address, txout.amount)
        
    # unspentTxOuts_additional = [*map(lambda tx: \
    #     list(map(local_build_txout, enumerate(tx.txOuts))), \
    #     newTransactions)]
    
    unspentTxOuts_additional = [*map(lambda tx: \
        [UnspentTxOut(tx.id, idx, txout.address, txout.amount) for idx, txout in enumerate(tx.txOuts)], \
        newTransactions)]
    
    # Reduced:
    unspentTxOuts_additional = sum(list(unspentTxOuts_additional), [])
    
    # Get all of the txIns of new transactions, merge into one list
    spentTxOuts: list[UnspentTxOut] = list(map(lambda x: x.txIns, newTransactions))
    spentTxOuts = sum(spentTxOuts, [])
    spentTxOuts = list(map(lambda txin: UnspentTxOut(txin.outId, txin.outIndex, '', 0), spentTxOuts))
    
    # Determine full set of unspent txouts by adding new txouts and removing spent ones
    # newUnspentTxOuts: list[UnspentTxOut] = list(filter(lambda utxo: \
    #     not findUnspentTxOut(utxo._txOutId, utxo._txOutIndex, spentTxOuts),unspentTxOuts))
    
    newUnspentTxOuts = []
    for utxo in unspentTxOuts:
        if not findUnspentTxOut(utxo._txOutId, utxo._txOutIndex, spentTxOuts):
            newUnspentTxOuts.append(utxo)
        
    newUnspentTxOuts.extend(unspentTxOuts_additional)
    
    return newUnspentTxOuts
    

# Yeah this can be done later its boring
# TODO(Chris) this shit
def isValidTransactionStructure(tx: Transaction) -> bool:
    return True


# Validate a TxIn
def validateTxIn(txin: TxIn, tx: Transaction, unspentTxOuts: list[UnspentTxOut]) -> bool:
    referencedUTxO: UnspentTxOut
    referencedUTxO = next(filter(lambda utxo: \
        utxo._txOutId == txin.outId, unspentTxOuts))
    
    if not referencedUTxO:
        print("Referenced TxOut not found among specified UnspentTxOuts.")
        return False
    
    address = referencedUTxO._address
    
    verifying_key = VerifyingKey.from_string(bytearray.fromhex(address))
    signature_bytes = bytearray.fromhex(txin.signature)
    retval = verifying_key.verify(signature_bytes, tx.id.encode())
    return retval


def getTxInAmount(txIn: TxIn, unspentTxOuts: list[UnspentTxOut]) -> float:
    return findUnspentTxOut(txIn.outId, txIn.outIndex, unspentTxOuts)._amount


# Validate a full Transaction
def validateTransaction(tx: Transaction, unspentTxOuts: list[UnspentTxOut]) -> bool:
    if not isValidTransactionStructure(tx):
        print("TX structure is invalid")
        return False
    
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


def validateCoinbaseTX(tx: Transaction, index: int) -> bool:
    if not tx:
        print("TX is null")
        return False
    
    if getTransactionId(tx) != tx.id:
        print("TXID is invalid")
        return False
    
    if len(tx.txIns) != 1:
        print("Coinbase TX requires exactly 1 input")
        return False
    
    if tx.txIns[0].outIndex != index:
        print("Coinbase TX must include index and match block index")
        return False
    
    if len(tx.txOuts) != 1:
        print("Coinbase TX requires exactly 1 output.")
        return False
    
    if tx.txOuts[0].amount != COINBASE_PAYOUT:
        print("Coinbase amount is invalid.")
        return False
    
    return True


def validateFullBlockTransactions(txs: list[Transaction], unspentTxOuts: list[UnspentTxOut], index: int) -> bool:
    coinbase = txs[0]
    if not validateCoinbaseTX(coinbase, index):
        print("Invalid coinbase tx")
        return False
    
    for tx in txs:
        for i in range(0,len(tx.txIns)-1):
            for j in range(i, len(tx.txIns)):
                if str(tx.txIns[i]) == str(tx.txIns[j]):
                    print("Duplicate txin")
                    return False
    
    nonCoinbase = txs[1:]
    for i in range(0, len(nonCoinbase)):
        nonCoinbase[i] = validateTransaction(nonCoinbase[i], unspentTxOuts)
    
    # Only if all TXs are valid
    return all(nonCoinbase)


def processTransactions(txs: list[Transaction], unspentTxOuts: list[UnspentTxOut], index: int):
    for tx in txs:
        if not isValidTransactionStructure(tx):
            print("borked")
            return None
    
    if not validateFullBlockTransactions(txs, unspentTxOuts, index):
        print("Invalid transactions in block")
        return None
    
    return updateUnspent(txs, unspentTxOuts)
    
    

def makeCoinbaseTX(address: str, index: int) -> Transaction:
    tx: Transaction = Transaction()
    txin: TxIn = TxIn("", index, "")
    
    tx.txIns = [txin]
    txout = TxOut(address, COINBASE_PAYOUT)
    tx.txOuts = [txout]
    tx.id = getTransactionId(tx)
    
    return tx

    
# DESERIALIZATION
def deserialize_txin(txin: dict) -> TxIn:
    outid = txin['outId']
    outIndex = txin['outIndex']
    signature = txin['signature']
    return TxIn(outid, outIndex, signature)

def deserialize_txout(txout: dict) -> TxOut:
    address = txout['address']
    amount = float(txout['amount'])
    return TxOut(address, amount)

def deserialize_tx(tx: dict) -> Transaction:
    txid = tx['id']
    txins = []
    for txin in tx['txIns']:
        txins.append(deserialize_txin(txin))
    
    txouts = []
    for txout in tx['txOuts']:
        txouts.append(deserialize_txout(txout))
    
    return Transaction(txid, txins, txouts)



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

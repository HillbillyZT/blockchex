from ecdsa import SigningKey
from hashlib import sha256
from functools import reduce


class TxOut:
    def __init__(self, address: str, amount: float) -> None:
        self.address = address
        self.amount = amount


class TxIn:
    def __init__(self, outId: str, outIndex: int, signature: str) -> None:
        self.outId = outId
        self.outIndex = outIndex
        self.signature = signature


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


def getTransactionId(tx: Transaction) -> str:
    txInsStr: str = reduce(lambda x, y: x + y, map(lambda a: str(a.outId) + str(a.outIndex), tx.txIns))
    txOutStr: str = reduce(lambda x, y: x + y, map(lambda a: str(a.address) + str(a.amount), tx.txOuts))
    unencoded: str = txInsStr + txOutStr
    hash = sha256(unencoded.encode()).hexdigest()
    return hash


def findUnspentTxOut(txId: str, index: int, unspentTxOuts: list[UnspentTxOut]) -> TxOut:
    return filter(lambda utxo: utxo._txOutId == txId and utxo._txOutIndex == index, unspentTxOuts)[0]


def makePrivateKey() -> SigningKey:
    return SigningKey.generate()


def getPublicKey(privateKey: str) -> str:
    return SigningKey.from_string(privateKey).verifying_key


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


# Testing

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

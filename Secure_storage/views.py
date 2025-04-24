import base64
import ipfshttpclient
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from web3 import Web3
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
from dotenv import load_dotenv

# load .env configuration
load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")
# IPFS connection
try:
    ipfs = ipfshttpclient.connect()
except Exception as e:
    raise Exception(f"IPFS connection failed:{str(e)}")
# Ethereum connection
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
# Smart Contract ABI
ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "ipfsHash", "type": "string"},
            {"internalType": "string", "name": "nonce", "type": "string"},
            {"internalType": "string", "name": "tag", "type": "string"},
        ],
        "name": "storeFile",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getFiles",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "ipfsHash", "type": "string"},
                    {"internalType": "string", "name": "nonce", "type": "string"},
                    {"internalType": "string", "name": "tag", "type": "string"},
                ],
                "internalType": "struct Storage.File[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
]
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
# AES-GCM Encryption
def encrypt_file(data: bytes, key: bytes):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
    }
def decrypt_file(enc_data, key):
    nonce = base64.b64decode(enc_data["nonce"])
    tag = base64.b64decode(enc_data["tag"])
    ciphertext = base64.b64decode(enc_data["ciphertext"])
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
# ipfs functions
def upload_to_ipfs(data: bytes):
    return ipfs.add_bytes(data)

def download_from_ipfs(ipfs_hash: str):
    return ipfs.cat(ipfs_hash)

# Upload view
@csrf_exempt
@require_POST
def upload_secure_file(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "File not provided"}, status=400)
    if uploaded_file.size > 10 * 1024 * 1024:
        return JsonResponse({"error": "File size exceeds 10MB"}, status=400)
    file_data = uploaded_file.read()
    key = get_random_bytes(32)
    encrypted = encrypt_file(file_data, key)
    ciphertext = base64.b64decode(encrypted["ciphertext"])
    try:
        ipfs_hash = upload_to_ipfs(ciphertext)
    except Exception as e:
        return JsonResponse({"error": f"IPFS upload failed:{str(e)}"}, status=500)
    try:
        tx = contract.function.storeFile(
            ipfs_hash, encrypted["nonce"], encrypted["tag"]
        ).build_transaction(
            {
                "from": ACCOUNT_ADDRESS,
                "nonce": w3.eth.get_transaction_count(ACCOUNT_ADDRESS),
                "gas": 300000,
                "gasPrice": w3.to_wei("10", "gwei"),
            }
        )
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        return JsonResponse({"error": f"Blockchain TX failed:{str(e)}"}, status=500)
    return JsonResponse(
        {
            "ipfs_hash": ipfs_hash,
            "ipfs_url": f"https://ipfs.io/ipfs/{ipfs_hash}",
            "nonce": encrypted["nonce"],
            "tag": encrypted["tag"],
            "encryption_key": base64.b64encode(key).decode(),
        }
    )
# Retrieve view
@csrf_exempt
@require_POST
def retrieve_secure_file(request):
    ipfs_hash = request.POST.get("ipfs_hash")
    key_encoded = request.POST.get("key")
    nonce = request.POST.get("nonce")
    tag = request.POST.get("tag")
    if not all([ipfs_hash, key_encoded, nonce, tag]):
        return JsonResponse({"error": "Missing parameters"}, status=400)
    try:
        key = base64.b64decode(key_encoded)
        ciphertext = download_from_ipfs(ipfs_hash)
        enc_data = {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "nonce": nonce,
            "tag": tag,
        }
        decrypted = decrypt_file(enc_data, key)
        return JsonResponse({"file": base64.b64encode(decrypted).decode()})
    except Exception as e:
        return JsonResponse({"error": f"Decryption failed:{str(e)}"}, status=400)

import argparse
parser = argparse.ArgumentParser("new_device_registration")
parser.add_argument("internet_identity_anchor", help="A new device 'python_scripts' will be added to the Internet Identity anchor provided", type=str)
args = parser.parse_args()

try:
  internet_identity_anchor = int(args.internet_identity_anchor)
except:
  import internet_identity_names
  internet_identity_anchor = internet_identity_names.names[args.internet_identity_anchor]

# you will need the ed25519 Python package
import ed25519
signing_key, verifying_key = ed25519.create_keypair()
public_key = verifying_key.to_ascii(encoding="hex") 
private_key = signing_key.to_ascii(encoding="hex").decode('utf-8') 

# WARNING: this saves your private key to the local repo
# PLEASE, do not commit this to Github
# If you commit this to a public repo, someone could easily steal your entire II
with open(f'{internet_identity_anchor}_internet_identity_private_key.txt','w') as f:
    f.write(private_key)

# candid included here as ic-py doesn't support inline Type definitions yet
with open('./identity.did','r') as f:
    identity_canister_did = f.read()

##############################

from ic.canister import Canister
from ic.client import Client
from ic.agent import Agent
from ic.identity import Identity

device_identity = Identity(private_key)
device_client = Client(url = "https://ic0.app")
device_agent = Agent(device_identity, device_client)

identity_canister_id = 'rdmx6-jaaaa-aaaaa-aaadq-cai' #identity canister
identityCanister = Canister(agent=device_agent, canister_id=identity_canister_id, candid=identity_canister_did)

################################

response = identityCanister.add_tentative_device(internet_identity_anchor,
    {
      'pubkey':device_identity.der_pubkey,
      'alias':'python_scripts',
      'credential_id':[[]],
      'purpose':{'authentication':None},
      'key_type':{'unknown':None}
  }
)
print(response)
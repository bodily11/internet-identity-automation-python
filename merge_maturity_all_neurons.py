import argparse
parser = argparse.ArgumentParser("merge_maturity")
parser.add_argument("internet_identity_anchor", help="All neurons for this Internet Identity anchor will have their maturity merged", type=str)
args = parser.parse_args()


try:
  internet_identity_anchor = int(args.internet_identity_anchor)
except:
  import internet_identity_names
  internet_identity_anchor = internet_identity_names.names[args.internet_identity_anchor]

import json
from ic.canister import Canister
from ic.client import Client
from ic.agent import Agent
from ic.identity import Identity
from ic.identity import DelegateIdentity


with open('./identity.did','r') as f:
    identity_canister_did = f.read()

with open('./governance.did','r') as f:
    governance_did = f.read()

with open(f'./{internet_identity_anchor}_internet_identity_private_key.txt','r') as f:
    private_key = f.read()

device_identity = Identity(private_key)
new_public_key = device_identity.der_pubkey
save_iden = device_identity.privkey + device_identity.pubkey

device_client = Client(url = "https://ic0.app")
device_agent = Agent(device_identity, device_client)

identity_canister_id = 'rdmx6-jaaaa-aaaaa-aaadq-cai' #identity canister
identityCanister = Canister(agent=device_agent, canister_id=identity_canister_id, candid=identity_canister_did)

delegation_result = identityCanister.prepare_delegation(
    internet_identity_anchor,
    'https://nns.ic0.app',
    new_public_key,
    [604800000000000]
)

result = identityCanister.get_delegation(
    internet_identity_anchor,
    'https://nns.ic0.app',
    new_public_key,
    delegation_result[1]
)

ic_delegation = {}
ic_delegation['delegations'] = [result[0]['signed_delegation']]
ic_delegation['publicKey'] = delegation_result[0]
ic_identity = [new_public_key.hex(),
               save_iden]

ic_delegation['delegations'][0]['signature'] = bytes(ic_delegation['delegations'][0]['signature']).hex()
ic_delegation['delegations'][0]['delegation']['pubkey'] = bytes(ic_delegation['delegations'][0]['delegation']['pubkey']).hex()
ic_delegation['delegations'][0]['delegation']['expiration'] = hex(ic_delegation['delegations'][0]['delegation']['expiration'])
ic_delegation['publicKey'] = bytes(ic_delegation['publicKey']).hex()

delegated_client = Client(url = "https://ic0.app")
delegated_identity = DelegateIdentity.from_json(json.dumps(ic_identity), json.dumps(ic_delegation))
delegated_agent = Agent(delegated_identity, delegated_client)

governance_canister_id = 'rrkah-fqaaa-aaaaa-aaaaq-cai' #governance canister
governanceCanister = Canister(agent=delegated_agent, canister_id=governance_canister_id, candid=governance_did)

all_neuron_ids = governanceCanister.get_neuron_ids()[0]

all_neuron_info = governanceCanister.list_neurons({
    'neuron_ids':all_neuron_ids,
    'include_neurons_readable_by_caller':True
})

neurons_with_icp = [x for x in all_neuron_info[0]['neuron_infos'] if x[1]['stake_e8s'] > 0]

all_icp_neurons = [x[0] for x in neurons_with_icp]

for icp_neuron in all_icp_neurons:
    result = governanceCanister.manage_neuron(
        {
        'id':[{
            'id':icp_neuron
        }],

        'command':[{'MergeMaturity':{
            'percentage_to_merge':100
            }
        }],

        'neuron_id_or_subaccount':[]
        })
    print(result)
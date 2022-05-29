import argparse
parser = argparse.ArgumentParser("reject_proposals")
parser.add_argument("internet_identity_anchor", help="All neurons for this Internet Identity anchor will vote against spam proposals", type=int)
args = parser.parse_args()

internet_identity_anchor = int(args.internet_identity_anchor)

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

with open('./internet_identity_private_key.txt','r') as f:
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

result = governanceCanister.get_pending_proposals()
active_governance_proposals = [x for x in result[0] if x['topic'] == 4]

known_list_of_spammers = [16392997059792243989] #ysyms

for active_proposal in active_governance_proposals:
    if active_proposal['proposer'][0]['id'] in known_list_of_spammers: # check if neuron submitter in list of spammers
        for voting_neuron in active_proposal['ballots']: # loop through all voting neurons
            if voting_neuron[1]['vote'] == 0: # check that neuron hasn't voted on the proposal yet
                voting_neuron_id = voting_neuron[0]
                proposal_id = active_proposal['id'][0]['id']
                result = governanceCanister.manage_neuron(
                    {
                    'id':[{
                        'id':voting_neuron_id
                    }],
                    'command':[{
                        'RegisterVote':{
                            'vote':2, # 2 to reject
                            'proposal':[{
                                'id':proposal_id
                            }]
                        }
                    }],
                    'neuron_id_or_subaccount':[]
                    })
                print(result)
            else:
                pass
    else:
        pass #actual governance proposal, no automatic voting
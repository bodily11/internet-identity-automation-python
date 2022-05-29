import argparse
parser = argparse.ArgumentParser("new_device_registration")
parser.add_argument("internet_identity_anchor", help="A new device 'python_scripts' will be added to the Internet Identity anchor provided", type=int)
args = parser.parse_args()

internet_identity_anchor = int(args.internet_identity_anchor)

# you will need the ed25519 Python package
import ed25519
signing_key, verifying_key = ed25519.create_keypair()
vkey_hex = verifying_key.to_ascii(encoding="hex") #public key
sign_hex = signing_key.to_ascii(encoding="hex").decode('utf-8') #private key

# WARNING: this saves your private key to the local repo
# PLEASE, do not commit this to Github
# If you commit this to a public repo, someone could easily steal your entire II
with open(f'internet_identity_private_key.txt','w') as f:
    f.write(sign_hex)

##############################

# candid included here as ic-py doesn't support inline Type definitions yet
identity_canister_did = '''
  type verification_code = text;
  type maxTimeToLive = opt nat64;
  type UserNumber = nat64;
  type PublicKey = blob;
  type CredentialId = blob;
  type DeviceKey = PublicKey;
  type UserKey = PublicKey;
  type SessionKey = PublicKey;
  type FrontendHostname = text;
  type Timestamp = nat64;

  type HeaderField = record { text; text; };
  type request = HttpRequest;
  type HttpRequest = record {
    method: text;
    url: text;
    headers: vec HeaderField;
    body: blob;
  };

  type HttpResponse = record {
    status_code: nat16;
    headers: vec HeaderField;
    body: blob;
    streaming_strategy: opt StreamingStrategy;
  };

  type StreamingCallbackHttpResponse = record {
    body: blob;
    token: opt Token;
  };

  type Token = record {};

  type StreamingStrategy = variant {
    Callback: record {
      callback: func (Token) -> (StreamingCallbackHttpResponse) query;
      token: Token;
    };
  };

  type Purpose = variant {
      recovery;
      authentication;
  };

  type KeyType = variant {
      unknown;
      platform;
      cross_platform;
      seed_phrase;
  };

  type Challenge = record {
      png_base64: text;
      challenge_key: ChallengeKey;
  };

  type DeviceData = record {
    pubkey : DeviceKey;
    alias : text;
    credential_id : opt CredentialId;
    purpose: Purpose;
    key_type: KeyType;
  };

  type RegisterResponse = variant {
    // A new user was successfully registered.
    registered: record { user_number: UserNumber; };
    // No more registrations are possible in this instance of the II service canister.
    canister_full;
    // The challenge was not successful.
    bad_challenge;
  };

  type AddTentativeDeviceResponse = variant {
    // The device was tentatively added.
    added_tentatively: record { verification_code: text; device_registration_timeout: Timestamp;};
    // Device registration mode is off, either due to timeout or because it was never enabled.
    device_registration_mode_off;
    // There is another device already added tentatively
    another_device_tentatively_added;
  };

  type VerifyTentativeDeviceResponse = variant {
    // The device was successfully verified.
    verified;
    // Wrong verification code entered. Retry with correct code.
    wrong_code: record { retries_left: nat8};
    // Device registration mode is off, either due to timeout or because it was never enabled.
    device_registration_mode_off;
    // There is no tentative device to be verified.
    no_device_to_verify;
  };

  type Delegation = record {
    pubkey: PublicKey;
    expiration: Timestamp;
    targets: opt vec principal;
  };

  type SignedDelegation = record {
    delegation: Delegation;
    signature: blob;
  };

  type GetDelegationResponse = variant {
    // The signed delegation was successfully retrieved.
    signed_delegation: SignedDelegation;

    // The signature is not ready. Maybe retry by calling `prepare_delegation`
    no_such_delegation
  };

  type InternetIdentityStats = record {
    users_registered: nat64;
    assigned_user_number_range: record { nat64; nat64; };
  };

  type InternetIdentityInit = record {
    assigned_user_number_range : record { nat64; nat64; };
  };

  type ChallengeKey = text;

  type ChallengeResult = record {
      key : ChallengeKey;
      chars : text;
  };

  type DeviceRegistrationInfo = record {
      tentative_device : opt DeviceData;
      expiration: Timestamp;
  };

  type IdentityAnchorInfo = record {
      devices : vec DeviceData;
      device_registration: opt DeviceRegistrationInfo;
  };

  service : {
    init_salt: () -> ();
    create_challenge : () -> (Challenge);
    register : (DeviceData, ChallengeResult) -> (RegisterResponse);
    add : (UserNumber, DeviceData) -> ();
    remove : (UserNumber, DeviceKey) -> ();
    lookup : (UserNumber) -> (vec DeviceData) query;
    get_anchor_info : (UserNumber) -> (IdentityAnchorInfo);
    get_principal : (UserNumber, FrontendHostname) -> (principal) query;
    stats : () -> (InternetIdentityStats) query;
    enter_device_registration_mode : (UserNumber) -> (Timestamp);
    exit_device_registration_mode : (UserNumber) -> ();
    add_tentative_device : (UserNumber, DeviceData) -> (AddTentativeDeviceResponse);
    verify_tentative_device : (UserNumber, verification_code) -> (VerifyTentativeDeviceResponse);
    prepare_delegation : (UserNumber, FrontendHostname, SessionKey, maxTimeToLive) -> (UserKey, Timestamp);
    get_delegation: (UserNumber, FrontendHostname, SessionKey, Timestamp) -> (GetDelegationResponse) query;
    http_request: (request) -> (HttpResponse) query;
  }
'''

##############################

from ic.canister import Canister
from ic.client import Client
from ic.agent import Agent
from ic.identity import Identity

device_identity = Identity(sign_hex)
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
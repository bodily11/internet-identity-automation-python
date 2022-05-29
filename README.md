# internet-identity-automation-python
Add a scripts device to Internet Identity and use delegation to automate Internet Identity apps.

Potential use cases include:
1. Rescue an NFT that has been transferred to an NNS wallet address
2. Automatically merge maturity on your neurons every day
3. Automatically reject NNS proposals from known spammers
4. Post to a social media site
5. Batch transfer NFTs (if using II to login to Stoic)

# Setup your environment
1. You need an installation of Python 3
2. You need to git clone the ic-py repo and run "pip install ./" within the ic-py directory
3. You need to pip install the ed25519 Python package via "pip install ed25519"

# Usage is as follows:
## First, add a locally generated private key 'python_scripts' device to Internet Identity
1. Login to identity.ic0.app with the internet identity anchor you would like to automate
2. Click "Add device"
3. Select "Remote Device"
4. At this point, you have 15 minutes to run the add_internet_identity_device.py python script in the repo. First, navigate to the internet-identity-automation-python directory. Then run this command: "python add_internet_identity_device.py 1068431". Where 1068431 is changed to the internet identity anchor you would like to automate.
5. Step #4 will print a verification code in the terminal. Paste that verification code back on the identity.ic0.app device registration page to complete adding the device.
6. Congrats, you have successfully generated an ed25519 private key, saved it to your computer, and added it as a device to your Internet Identity.

Note: this private key has FULL control over your entire internet identity. If you commit the private key to a public GitHub repo, or paste it online, a hacker could lock you out of your Internet Identity completely. So please keep it safe.

## Next, feel free to run any of the automated scripts in the library
At this point, you can choose from the following automations:
1. merge_maturity_all_neurons.py: Merge maturity for all neurons for a specific Internet Identity anchor
2. reject_proposals_from_known_spammers.py: Reject all governance proposals that have been proposed by a known NNS spammer

These automations are easily run using the following syntax within the internet-identity-automation-python repo:
"python script_you_want_to_call.py 1068431" where 1068431 is changed to the internet identity anchor you would like to automate.

# Contribute!
If you find bugs or would like to add automations to this repo, please submit a PR! I'll be adding more automations to the library over the next few months and would love to have contributions from others doing the same.

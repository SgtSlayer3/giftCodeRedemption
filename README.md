**Gift Code Redeemer for list of IDs**

**Process:**
- Reads player IDs and usernames from a playerIDs.txt file.
- Automatically fills in player IDs and a gift code.
- Clicks through the login and confirm steps for each player.
- Logs progress in the terminal.
- Takes a screenshot if redemption fails for any player.

**File Structure:**
.
├── giftCodeRedeem.py      # Main script
├── playerIDs.txt          # Input file containing player IDs and usernames
└── README.md              # This file

**Requirements:**
pip install selenium webdriver-manager

**Input Format:**
playerIDs.txt must be formated like this:
123456789 Username1
987654321 Username2

**Usage:**
Edit the gift_code value on line 10.
Run the script:
  python giftCodeRedeem.py

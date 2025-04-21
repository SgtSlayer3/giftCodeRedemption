**Gift Code Redeemer for list of IDs**
Allows one user to efficiently redeem new codes for their entire alliance or an entire state.

**Process:**
- Reads player IDs and usernames from a playerIDs.txt file.
- Automatically fills in player IDs and the gift code.
- Clicks through the login and confirm steps for each player.
- Logs progress to log.txt.
- Takes a screenshot if redemption fails for any player.

**File Structure:**
.
├── giftCodeRedeem.py      # Main script
├── playerIDs.txt          # Input file containing player IDs and usernames
├── log.txt                # Log file with output
└── README.md              # This file

**Requirements:**
- pip install selenium webdriver-manager
- Google Chrome
- Python 3.7+

**Input Format:**
playerIDs.txt must be formated like this:
123456789 Username1
987654321 Username2

**Usage:**
- Clone the repository:  
  `git clone https://github.com/SgtSlayer3/giftCodeRedemption.git`
- Navigate into the folder:  
  `cd gift-code-redeemer`
- Edit `playerIDs.txt` with your real data  
- Run the script:  
  `python giftCodeRedeem.py`
- Enter the gift code when prompted. Be sure to get this right as invalid codes will still run.
- IDs are printed to `log.txt`

**Other notes:**
- There is very limited error checking if there is an invalid ID or code it will still run with no warnings.
- Any fails check the corresponding debug_<PlayerID>_error.png
- If you are having issues with a "Busy server" increase the sleep times

---

**Author:** SgtSlayer    
**Project Link:** [GitHub repository](https://github.com/SgtSlayer3/giftCodeRedemption.git)

"""
Automated Gift Code Redemption Script

This script automates the process of redeeming a gift codes for players
on the Century Games gift code website (https://ks-giftcode.centurygame.com/)
for a list of player IDs provided in 'playerIDs.txt'. The same gift code is
applied to all players. Logs of each redemption attempt are saved in 'log.txt'.

Author: SgtSlayer
Date: 4/20/2025
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys

#Prompt the user for the gift code
gift_code = input("Enter the gift code to redeem: ").strip()

#Clear log file
log_file = "log.txt"
with open(log_file, "w", encoding="utf-8") as log:
    log.write("Gift Code Redemption Log\n\n")

#Print to log file
def log_print(*args, **kwargs):
    with open(log_file, "a", encoding="utf-8") as log:
        print(*args, **kwargs, file=log)
    #print(*args, **kwargs)  # Uncomment this line to print to console as well

#Read player IDs and usernames from the file
player_data = []
with open("playerIDs.txt", "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            pid, username = parts
            player_data.append((pid, username))

options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Uncomment this line to run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

wait = WebDriverWait(driver, 10)
start_time = time.time()
count = 0

for pid, username in player_data:
    count += 1
    driver.get("https://ks-giftcode.centurygame.com/") #website URL
    success = False

    try:
        #Wait for the page to loadt
        player_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//input[@placeholder="Player ID"]')
        ))
        player_input.clear()
        player_input.send_keys(pid) # Enter Player ID
        log_print(f"Entered Player ID: {pid} ({username})")

        #Wait for the username input field to be present
        code_input = driver.find_element(By.XPATH, '//input[@placeholder="Enter Gift Code"]')
        code_input.clear()
        code_input.send_keys(gift_code) # Enter Gift Code
        log_print("Entered Gift Code.")

        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[contains(@class, "login_btn") and contains(@class, "btn")]')
        ))
        login_button.click() # Click the login button
        log_print(f"Clicked Login for: {pid} ({username})")

        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, '//div[contains(@class, "loading-overlay-class")]')
        ))
        log_print(f"Login completed for: {pid} ({username})")

        time.sleep(1) # Wait for the page to load
        confirm_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[contains(@class, "exchange_btn") and contains(text(), "Confirm")]')
        ))
        driver.execute_script("arguments[0].click();", confirm_button)
        success = True

    except Exception as e:
        log_print(f"[!] Failed for Player ID: {pid} ({username}) — {e}")
        driver.save_screenshot(f"debug_{pid}_{username}_error.png")
        time.sleep(2)

    if success:
        log_print(f"[✓] Code redeemed for Player ID: {pid} ({username})\n")
    else:
        log_print(f"[✗] Redemption failed for Player ID: {pid} ({username})\n")

    time.sleep(1) # Wait for the confirmation message to appear

end_time = time.time()
log_print(f"\nProcessed {count} players in {end_time - start_time:.2f} seconds.")
print(f"\nProcessed {count} players in {end_time - start_time:.2f} seconds.")

driver.quit()

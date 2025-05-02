#!/usr/bin/env python3
"""
Automated Gift Code Redemption Script

This script automates the process of redeeming gift codes for players
on the Century Games gift code website (https://ks-giftcode.centurygame.com/)
in bulk from a list of player IDs provided in a text file. Logs are saved
both to the console and a log file, and failure screenshots are stored in
a dedicated directory.

Author: SgtSlayer (refactored)
Date: 2025-04-21
"""

import argparse
import logging
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def setup_logger(log_file: str) -> None:
    """Configure root logger to log INFO to console and file."""
    handlers = [logging.StreamHandler(sys.stdout), logging.FileHandler(log_file, encoding='utf-8')]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

def get_driver(headless: bool) -> webdriver.Chrome:
    """Instantiate a Chrome WebDriver with optional headless mode."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def read_player_data(input_file: str) -> list[tuple[str, str]]:
    """Read player IDs and usernames from a text file."""
    players = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                players.append((parts[0], parts[1]))
            else:
                logging.warning("Skipping malformed line: %s", line.strip())
    return players

def redeem_code(driver: webdriver.Chrome, wait: WebDriverWait,
                pid: str, username: str, gift_code: str,
                screenshot_dir: str) -> bool:
    """Attempt to redeem a single gift code for a player; takes screenshot on error."""
    driver.get("https://ks-giftcode.centurygame.com/")

    try:
        player_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Player ID']")
        ))
        player_input.clear()
        player_input.send_keys(pid)
        logging.info("Entered Player ID: %s (%s)", pid, username)

        code_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Enter Gift Code']")
        code_input.clear()
        code_input.send_keys(gift_code)
        logging.info("Entered Gift Code '%s' for %s", gift_code, pid)

        login_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".login_btn.btn")
        ))
        login_btn.click()
        logging.info("Clicked redeem for %s", pid)

        wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".loading-overlay-class")
        ))

        confirm_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'exchange_btn') and normalize-space()='Confirm']")
        ))
        driver.execute_script("arguments[0].click();", confirm_btn)
        logging.info("Confirmed gift code for %s", pid)
        return True

    except Exception as e:
        # Ensure screenshot directory exists before saving
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"error_{pid}_{gift_code}.png")
        driver.save_screenshot(screenshot_path)
        logging.error("Failed for %s (%s) with gift code '%s': %s. Screenshot: %s", pid, username, gift_code, e, screenshot_path)
        return False

def main(args=None) -> None:
    parser = argparse.ArgumentParser(
        description='Bulk redeem gift codes on Century Games.'
    )
    parser.add_argument('-c', '--code',
                        help='A single gift code to redeem.')
    parser.add_argument('-i', '--input', default='playerIDs.txt',
                        help='Path to input file with player IDs and usernames.')
    parser.add_argument('-l', '--log', default='log.txt',
                        help='Path to log file.')
    parser.add_argument('-s', '--screenshots', default='screenshots',
                        help='Directory to save failure screenshots.')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode.')

    if args is None:
        args = sys.argv[1:]

    parsed_args = parser.parse_args(args)

    # Setup directories early
    os.makedirs(parsed_args.screenshots, exist_ok=True)

    setup_logger(parsed_args.log)

    # Determine gift codes list
    codes_file = 'giftCodes.txt'
    if os.path.isfile(codes_file):
        with open(codes_file, 'r', encoding='utf-8') as cf:
            gift_codes = [line.strip() for line in cf if line.strip()]
        logging.info("Loaded %d gift codes from %s", len(gift_codes), codes_file)
    elif parsed_args.code:
        gift_codes = [parsed_args.code]
    else:
        code_input = input("Enter the gift code to redeem: ").strip()
        gift_codes = [code_input]

    players = read_player_data(parsed_args.input)
    if not players:
        logging.error("No valid player data found. Exiting.")
        sys.exit(1)

    driver = get_driver(parsed_args.headless)
    wait = WebDriverWait(driver, 10)
    overall_start = time.time()
    total_processed = 0
    total_success = 0

    for gift_code in gift_codes:
        logging.info("Starting redemption for gift code: %s", gift_code)
        start = time.time()
        failed_players = []

        for pid, username in players:
            total_processed += 1
            for attempt in range(1, 4):
                if redeem_code(driver, wait, pid, username, gift_code, parsed_args.screenshots):
                    total_success += 1
                    break
                logging.warning("Retry %d for %s with code %s", attempt + 1, pid, gift_code)
                time.sleep(2)
            else:
                failed_players.append((pid, username))

            time.sleep(1)

        elapsed = time.time() - start
        logging.info("Finished code '%s': %d succeeded, %d failed in %.2f seconds.",
                     gift_code, len(players) - len(failed_players), len(failed_players), elapsed)
        if failed_players:
            failed_file = f'failed_{gift_code}.txt'
            with open(failed_file, 'w', encoding='utf-8') as ff:
                for pid, username in failed_players:
                    ff.write(f"{pid} {username}\n")
            logging.warning("Failures logged to %s", failed_file)

    overall_elapsed = time.time() - overall_start
    logging.info("Processed %d total redemptions with %d successes in %.2f seconds.",
                 total_processed, total_success, overall_elapsed)
    driver.quit()

if __name__ == '__main__':
    main()

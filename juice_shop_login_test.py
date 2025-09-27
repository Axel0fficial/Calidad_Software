#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:3000"
WAIT = 15
EMAIL = "admin@example.com"
PASSWORD = "admin"

def start_driver(headless=False):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    d.set_window_size(1280, 900)
    return d

def dismiss_popups(driver):
    wait = WebDriverWait(driver, 3)
    # Close welcome banner (Juice Shop shows a top dialog)
    for sel in [
        "button[aria-label='Close Welcome Banner']",
        "button[aria-label='close welcome banner']",
        "button[aria-label='close cookie warning']",
        "button[aria-label='dismiss cookie message']",
        "button[aria-label='Close Dialog']",
    ]:
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel))).click()
            time.sleep(0.2)
        except Exception:
            pass

def open_login(driver):
    wait = WebDriverWait(driver, WAIT)
    # account menu
    for by, sel in [
        (By.ID, "navbarAccount"),
        (By.CSS_SELECTOR, "button[aria-label='Show/hide account menu']"),
        (By.CSS_SELECTOR, "button[aria-label='Account']"),
    ]:
        try:
            wait.until(EC.element_to_be_clickable((by, sel))).click()
            break
        except Exception:
            continue
    # login button in menu
    for by, sel in [
        (By.ID, "navbarLoginButton"),
        (By.CSS_SELECTOR, "button[aria-label='Login']"),
        (By.XPATH, "//button[contains(., 'Login')]"),
        (By.XPATH, "//a[contains(., 'Login')]"),
    ]:
        try:
            wait.until(EC.element_to_be_clickable((by, sel))).click()
            return
        except Exception:
            continue
    raise RuntimeError("Could not open login form")

def do_login(driver, email, password):
    wait = WebDriverWait(driver, WAIT)
    # Make sure we’re on the login page/dialog
    try:
        wait.until(EC.presence_of_element_located((By.ID, "email"))).clear()
        driver.find_element(By.ID, "email").send_keys(email)
        wait.until(EC.presence_of_element_located((By.ID, "password"))).clear()
        driver.find_element(By.ID, "password").send_keys(password)
        wait.until(EC.element_to_be_clickable((By.ID, "loginButton"))).click()
    except Exception:
        # Fallback selectors
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='email']"))).send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='password']").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

def wait_until_logged_in(driver):
    wait = WebDriverWait(driver, WAIT)
    # Best: wait for auth token in localStorage
    def token_present(drv):
        return drv.execute_script("return window.localStorage.getItem('token')") is not None
    try:
        wait.until(token_present)
        token = driver.execute_script("return window.localStorage.getItem('token')")
        print("Login OK — token present:", bool(token))
        return True
    except Exception:
        # Fallback: look for logout button
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "navbarLogoutButton")))
            print("Login OK — navbarLogoutButton present.")
            return True
        except Exception:
            return False

def go_to_profile(driver):
    # Navigate directly; avoids flaky menu clicks
    driver.get(f"{BASE_URL}/profile")
    wait = WebDriverWait(driver, WAIT)
    # Assert profile loaded (title or email shown)
    try:
        # typical heading in Profile page
        wait.until(EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//*[contains(., 'Your Profile')]")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "mat-card-title")),
        ))
        print("✅ Profile page opened.")
        return True
    except Exception:
        print("⚠️ Could not confirm profile; trying menu route once...")
        # Try via menu once if direct navigation didn’t show expected markers
        try:
            # open account menu
            WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, "navbarAccount"))).click()
            # click Your Profile
            for by, sel in [
                (By.XPATH, "//button[contains(., 'Your Profile')]"),
                (By.XPATH, "//a[contains(., 'Your Profile')]"),
                (By.CSS_SELECTOR, "button[aria-label='Go to user profile']"),
                (By.CSS_SELECTOR, "a[routerlink='/profile']"),
            ]:
                try:
                    WebDriverWait(driver, 6).until(EC.element_to_be_clickable((by, sel))).click()
                    print("Profile opened via menu.")
                    return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

def main():
    d = start_driver(headless=False)
    try:
        d.get(BASE_URL)
        dismiss_popups(d)
        open_login(d)
        do_login(d, EMAIL, PASSWORD)
        # small settle
        time.sleep(1.0)
        if not wait_until_logged_in(d):
            print("❌ Login not detected — check credentials/selectors.")
            time.sleep(4)
            return
        ok = go_to_profile(d)
        if not ok:
            print("❌ Failed to reach Profile page. Inspect selectors/UI.")
        else:
            # Optional: assert the email shows up somewhere
            try:
                WebDriverWait(d, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"//*[contains(text(),'{EMAIL.split('@')[0]}') or contains(text(),'{EMAIL}')]")
                    )
                )
                print("✅ Profile shows user info (email or username).")
            except Exception:
                print("ℹ️ Profile loaded but user info not found via quick check (may require different selector).")
        time.sleep(5)
    finally:
        d.quit()

if __name__ == "__main__":
    main()

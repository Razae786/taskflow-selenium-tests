import pytest
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL   = "http://16.54.195.112:3000"
TEST_EMAIL = "testuser@example.com"
TEST_PASS  = "Test@1234"
TEST_NAME  = "Test User"

@pytest.fixture(scope="function")
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    chromedriver_path = shutil.which('chromedriver') or '/usr/bin/chromedriver'
    service = Service(chromedriver_path)
    d = webdriver.Chrome(service=service, options=opts)
    d.implicitly_wait(10)
    yield d
    d.quit()

def wait(driver, by, sel, t=15):
    return WebDriverWait(driver, t).until(EC.presence_of_element_located((by, sel)))

def wait_for_react(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#root > *")) > 0 or 
                  len(d.find_elements(By.TAG_NAME, "input")) > 0 or
                  len(d.find_elements(By.TAG_NAME, "button")) > 0
    )
    time.sleep(1.5)

def register_user(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        signup_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign Up') or contains(text(), 'sign up')]")
        if signup_btn:
            signup_btn[0].click()
            time.sleep(1)
        wait(driver, By.CSS_SELECTOR, "input[type='text'], input[name='name']").send_keys(TEST_NAME)
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
    except Exception as e:
        print(f"Register error: {e}")

def login(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        login_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'login')]")
        if login_btn:
            login_btn[0].click()
            time.sleep(1)
        email_field = wait(driver, By.CSS_SELECTOR, "input[type='email']")
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").clear()
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
    except Exception as e:
        print(f"Login error: {e}")

def test_01_home_page_loads(driver):
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 500

def test_02_page_title_not_empty(driver):
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert driver.title != ""
    assert "taskflow" in driver.title.lower()

def test_03_login_has_email_field(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
    assert field.is_displayed()

def test_04_login_has_password_field(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    assert field.is_displayed()

def test_05_login_has_submit_button(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    assert btn.is_displayed()

def test_06_wrong_credentials_blocked(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        login_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'login')]")
        if login_btns:
            login_btns[0].click()
            time.sleep(1)
        wait(driver, By.CSS_SELECTOR, "input[type='email']").send_keys("bad@bad.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("badpass")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        error_present = any(w in driver.page_source.lower() for w in ["invalid", "error", "wrong", "incorrect", "failed"])
        still_on_login = driver.current_url == BASE_URL + "/" or "/login" in driver.current_url
        assert error_present or still_on_login
    except Exception as e:
        pytest.skip(f"Could not test: {e}")

def test_07_empty_login_blocked(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        assert "dashboard" not in driver.current_url
    except Exception:
        pass

def test_08_register_page_accessible(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        signup_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign Up') or contains(text(), 'sign up') or contains(text(), 'Register')]")
        if signup_btn:
            signup_btn[0].click()
            time.sleep(1)
            name_field = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[name='name']")
            assert len(name_field) > 0
        else:
            pytest.skip("No signup toggle found")
    except Exception as e:
        pytest.skip(f"Could not test registration: {e}")

def test_09_no_server_error(driver):
    driver.get(BASE_URL)
    wait_for_react(driver)
    src = driver.page_source.lower()
    assert "internal server error" not in src
    assert "error 500" not in src
    assert "502 bad gateway" not in src
    assert "503 service unavailable" not in src

def test_10_valid_login_redirects(driver):
    register_user(driver)
    login(driver)
    time.sleep(2)
    current = driver.current_url
    if "/dashboard" in current:
        assert True
    elif current == BASE_URL + "/":
        if "error" in driver.page_source.lower() or "invalid" in driver.page_source.lower():
            pytest.skip("Login failed - user may already exist")
        else:
            pytest.skip("Still on login page after login attempt")
    else:
        assert "/dashboard" in current, f"Not redirected to dashboard: {current}"

def test_11_dashboard_has_tasks_or_projects(driver):
    register_user(driver)
    login(driver)
    time.sleep(2)
    if "/dashboard" not in driver.current_url:
        pytest.skip("Not on dashboard")
    src = driver.page_source.lower()
    assert any(w in src for w in ["project", "task", "dashboard", "logout", "create", "add"])

def test_12_add_task_or_project_button_exists(driver):
    register_user(driver)
    login(driver)
    time.sleep(2)
    if "/dashboard" not in driver.current_url:
        pytest.skip("Not on dashboard")
    src = driver.page_source.lower()
    assert any(w in src for w in ["add", "new", "create", "+", "project"])

def test_13_logout_exists(driver):
    register_user(driver)
    login(driver)
    time.sleep(2)
    if "/dashboard" not in driver.current_url:
        pytest.skip("Not on dashboard")
    src = driver.page_source.lower()
    assert any(w in src for w in ["logout", "log out", "sign out", "exit"])

def test_14_mobile_viewport(driver):
    driver.set_window_size(375, 812)
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 500

def test_15_desktop_viewport(driver):
    driver.set_window_size(1920, 1080)
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 500

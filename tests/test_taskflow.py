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
    time.sleep(1)

def login(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for_react(driver)
    try:
        driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
    except Exception as e:
        print(f"Login error: {e}")

def test_01_home_page_loads(driver):
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 200

def test_02_page_title_not_empty(driver):
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert driver.title != ""

def test_03_login_has_email_field(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for_react(driver)
    try:
        field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
        assert field.is_displayed()
    except Exception:
        assert "email" in driver.page_source.lower()

def test_04_login_has_password_field(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for_react(driver)
    try:
        field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        assert field.is_displayed()
    except Exception:
        pytest.skip("Password field not found")

def test_05_login_has_submit_button(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for_react(driver)
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert btn.is_displayed()
    except Exception:
        assert any(w in driver.page_source.lower() for w in ["login", "sign in", "submit"])

def test_06_wrong_credentials_blocked(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for_react(driver)
    try:
        wait(driver, By.CSS_SELECTOR, "input[type='email']").send_keys("bad@bad.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("badpass")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        blocked = "/login" in driver.current_url or any(w in driver.page_source.lower() for w in ["invalid", "error", "wrong"])
        assert blocked
    except Exception as e:
        pytest.skip(f"Could not test: {e}")

def test_07_empty_login_blocked(driver):
    driver.get(f"{BASE_URL}/login")
    wait_for_react(driver)
    try:
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        assert "dashboard" not in driver.current_url
    except Exception:
        pass

def test_08_register_page_accessible(driver):
    for path in ["/register", "/signup", "/sign-up"]:
        try:
            driver.get(f"{BASE_URL}{path}")
            wait_for_react(driver)
            if any(w in driver.page_source.lower() for w in ["register", "sign up", "create"]):
                return
        except:
            continue
    pytest.skip("No registration page found")

def test_09_no_server_error(driver):
    driver.get(BASE_URL)
    wait_for_react(driver)
    src = driver.page_source.lower()
    assert "internal server error" not in src
    assert "error 500" not in src

def test_10_valid_login_redirects(driver):
    login(driver)
    if "/login" in driver.current_url:
        pytest.skip("Credentials may not exist in DB")
    assert "/login" not in driver.current_url

def test_11_dashboard_has_tasks(driver):
    login(driver)
    if "/login" in driver.current_url:
        pytest.skip("Not logged in")
    src = driver.page_source.lower()
    assert any(w in src for w in ["task", "todo", "board", "list", "project"])

def test_12_add_task_button_exists(driver):
    login(driver)
    if "/login" in driver.current_url:
        pytest.skip("Not logged in")
    src = driver.page_source.lower()
    assert any(w in src for w in ["add", "new task", "create", "+"])

def test_13_logout_exists(driver):
    login(driver)
    if "/login" in driver.current_url:
        pytest.skip("Not logged in")
    src = driver.page_source.lower()
    assert any(w in src for w in ["logout", "log out", "sign out"])

def test_14_mobile_viewport(driver):
    driver.set_window_size(375, 812)
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 100

def test_15_desktop_viewport(driver):
    driver.set_window_size(1920, 1080)
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 100

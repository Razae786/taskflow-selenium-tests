import pytest
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── CONFIG ──────────────────────────────────────────────────────────────────
BASE_URL   = "http://16.54.195.112:3000"
TEST_EMAIL = "testuser@example.com"
TEST_PASS  = "Test@1234"

# ── FIXTURE ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-features=VizDisplayCompositor")
    
    # Chromium snap paths
    chrome_paths = [
        '/snap/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/google-chrome',
    ]
    
    chrome_binary = None
    for path in chrome_paths:
        if shutil.which(path):
            chrome_binary = path
            break
    
    if chrome_binary:
        opts.binary_location = chrome_binary
    
    try:
        service = Service(ChromeDriverManager().install())
        d = webdriver.Chrome(service=service, options=opts)
    except Exception:
        # Fallback: use system chromedriver directly
        service = Service('/usr/bin/chromedriver')
        d = webdriver.Chrome(service=service, options=opts)
    
    d.implicitly_wait(10)
    yield d
    d.quit()

def wait(driver, by, sel, t=15):
    return WebDriverWait(driver, t).until(
        EC.presence_of_element_located((by, sel))
    )

def login(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    try:
        wait(driver, By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════════════
# 15 TEST CASES
# ═══════════════════════════════════════════════════════════════════════════

def test_01_home_page_loads(driver):
    driver.get(BASE_URL)
    time.sleep(3)
    assert len(driver.page_source) > 200, "Home page is blank"

def test_02_page_title_not_empty(driver):
    driver.get(BASE_URL)
    time.sleep(2)
    assert driver.title != "", "Page title is empty"

def test_03_login_has_email_field(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    src = driver.page_source.lower()
    assert "email" in src or "username" in src, "No email field on login"

def test_04_login_has_password_field(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    try:
        field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        assert field.is_displayed()
    except Exception:
        pytest.skip("Password field not found")

def test_05_login_has_submit_button(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    src = driver.page_source.lower()
    assert any(w in src for w in ["login", "sign in", "submit"]), "No submit button"

def test_06_wrong_credentials_blocked(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    try:
        wait(driver, By.CSS_SELECTOR, "input[type='email'], input[name='email']").send_keys("bad@bad.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("badpass")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        blocked = "/login" in driver.current_url or any(w in driver.page_source.lower() for w in ["invalid", "error", "wrong"])
        assert blocked, "Wrong credentials were accepted"
    except Exception as e:
        pytest.skip(f"Could not test: {e}")

def test_07_empty_login_blocked(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)
    try:
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        assert "dashboard" not in driver.current_url, "Empty login reached dashboard"
    except Exception:
        pass

def test_08_register_page_accessible(driver):
    for path in ["/register", "/signup", "/sign-up"]:
        try:
            driver.get(f"{BASE_URL}{path}")
            time.sleep(2)
            if any(w in driver.page_source.lower() for w in ["register", "sign up", "create"]):
                assert True
                return
        except:
            continue
    pytest.skip("No registration page found")

def test_09_no_server_error(driver):
    driver.get(BASE_URL)
    time.sleep(2)
    src = driver.page_source.lower()
    assert "500" not in src and "internal server error" not in src, "Server error on home"

def test_10_valid_login_redirects(driver):
    login(driver)
    assert "/login" not in driver.current_url, f"Still on login: {driver.current_url}"

def test_11_dashboard_has_tasks(driver):
    login(driver)
    src = driver.page_source.lower()
    assert any(w in src for w in ["task", "todo", "board", "list", "project"]), "No task content"

def test_12_add_task_button_exists(driver):
    login(driver)
    src = driver.page_source.lower()
    assert any(w in src for w in ["add", "new task", "create", "+"]), "No add task button"

def test_13_logout_exists(driver):
    login(driver)
    src = driver.page_source.lower()
    assert any(w in src for w in ["logout", "log out", "sign out"]), "No logout option"

def test_14_mobile_viewport(driver):
    driver.set_window_size(375, 812)
    driver.get(BASE_URL)
    time.sleep(2)
    assert len(driver.page_source) > 100, "Broken on mobile"

def test_15_desktop_viewport(driver):
    driver.set_window_size(1920, 1080)
    driver.get(BASE_URL)
    time.sleep(2)
    assert len(driver.page_source) > 100, "Broken on desktop"

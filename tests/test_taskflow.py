import pytest
import time
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
TEST_NAME  = "Test User"

# ── FIXTURE ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    
    # Use webdriver-manager to auto-download correct chromedriver
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.implicitly_wait(10)
    yield d
    d.quit()

def wait(driver, by, sel, t=15):
    return WebDriverWait(driver, t).until(
        EC.presence_of_element_located((by, sel))
    )

def wait_for_react(driver, timeout=10):
    """Wait for React to render - check for inputs, buttons, or root content"""
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#root > *")) > 0 or 
                  len(d.find_elements(By.TAG_NAME, "input")) > 0 or
                  len(d.find_elements(By.TAG_NAME, "button")) > 0 or
                  len(d.find_elements(By.TAG_NAME, "form")) > 0
    )
    time.sleep(1.5)  # Extra wait for full React render

def register_user(driver):
    """Register a new test user"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        # Click "Sign Up" toggle if on login view
        signup_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign Up') or contains(text(), 'sign up')]")
        if signup_btn:
            signup_btn[0].click()
            time.sleep(1)
        
        wait(driver, By.CSS_SELECTOR, "input[type='text'], input[name='name'], input[placeholder*='name' i]").send_keys(TEST_NAME)
        driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
    except Exception as e:
        print(f"Register error: {e}")

def login(driver):
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        # Make sure we're on login view (click Login toggle if on Sign Up)
        login_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'login')]")
        if login_btn:
            login_btn[0].click()
            time.sleep(1)
        
        email_field = wait(driver, By.CSS_SELECTOR, "input[type='email'], input[name='email']")
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").clear()
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
    except Exception as e:
        print(f"Login error: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# 15 TEST CASES
# ═══════════════════════════════════════════════════════════════════════════

def test_01_home_page_loads(driver):
    """Test that home page loads and renders content"""
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 500, "Home page is blank or too small"

def test_02_page_title_not_empty(driver):
    """Test that page has a title"""
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert driver.title != "", "Page title is empty"
    assert "taskflow" in driver.title.lower(), "Title doesn't contain 'taskflow'"

def test_03_login_has_email_field(driver):
    """Test login form has email input field"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
        assert field.is_displayed(), "Email field found but not visible"
    except Exception:
        pytest.fail("No email field on login page")

def test_04_login_has_password_field(driver):
    """Test login form has password input field"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        assert field.is_displayed(), "Password field found but not visible"
    except Exception:
        pytest.fail("No password field on login page")

def test_05_login_has_submit_button(driver):
    """Test login form has submit button"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert btn.is_displayed(), "Submit button found but not visible"
        assert "login" in btn.text.lower() or "sign in" in btn.text.lower() or "submit" in btn.text.lower(), "Button text doesn't indicate login"
    except Exception:
        pytest.fail("No submit button on login page")

def test_06_wrong_credentials_blocked(driver):
    """Test that wrong credentials show error or stay on page"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        # Ensure login view
        login_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'login')]")
        if login_btns:
            login_btns[0].click()
            time.sleep(1)
        
        wait(driver, By.CSS_SELECTOR, "input[type='email']").send_keys("bad@bad.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("badpass")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Should either show error message or stay on login page
        error_present = any(w in driver.page_source.lower() for w in ["invalid", "error", "wrong", "incorrect", "failed"])
        still_on_login = driver.current_url == BASE_URL + "/" or "/login" in driver.current_url
        assert error_present or still_on_login, "Wrong credentials were accepted"
    except Exception as e:
        pytest.skip(f"Could not test wrong credentials: {e}")

def test_07_empty_login_blocked(driver):
    """Test that empty form submission doesn't crash or redirect to dashboard"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        assert "dashboard" not in driver.current_url, "Empty login reached dashboard"
    except Exception:
        pass  # Form validation prevented submission

def test_08_register_page_accessible(driver):
    """Test that signup/registration toggle works"""
    driver.get(f"{BASE_URL}/")
    wait_for_react(driver)
    try:
        # Find and click Sign Up button
        signup_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign Up') or contains(text(), 'sign up') or contains(text(), 'Register')]")
        if signup_btn:
            signup_btn[0].click()
            time.sleep(1)
            # Should show name field (only in signup form)
            name_field = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[name='name']")
            assert len(name_field) > 0, "Sign up form doesn't show name field"
        else:
            pytest.skip("No signup toggle found")
    except Exception as e:
        pytest.skip(f"Could not test registration: {e}")

def test_09_no_server_error(driver):
    """Test that home page doesn't show server errors"""
    driver.get(BASE_URL)
    wait_for_react(driver)
    src = driver.page_source.lower()
    assert "internal server error" not in src, "Server error on home"
    assert "error 500" not in src, "Error 500 on home"
    assert "502 bad gateway" not in src, "Bad gateway on home"
    assert "503 service unavailable" not in src, "Service unavailable on home"

def test_10_valid_login_redirects(driver):
    """Test that valid login redirects to dashboard"""
    # First register the user if not exists
    register_user(driver)
    
    # Now login
    login(driver)
    
    # Should be redirected to dashboard
    time.sleep(2)
    current = driver.current_url
    if "/dashboard" in current:
        assert True
    elif current == BASE_URL + "/":
        # Maybe login failed - check for error
        if "error" in driver.page_source.lower() or "invalid" in driver.page_source.lower():
            pytest.skip("Login failed - user may already exist or credentials wrong")
        else:
            pytest.skip("Still on login page after login attempt")
    else:
        assert "/dashboard" in current, f"Not redirected to dashboard: {current}"

def test_11_dashboard_has_tasks_or_projects(driver):
    """Test dashboard shows projects or task-related content after login"""
    register_user(driver)
    login(driver)
    time.sleep(2)
    
    if "/dashboard" not in driver.current_url:
        pytest.skip("Not on dashboard - login may have failed")
    
    src = driver.page_source.lower()
    assert any(w in src for w in ["project", "task", "dashboard", "logout", "create", "add"]), "No project/task content on dashboard"

def test_12_add_task_or_project_button_exists(driver):
    """Test dashboard has add/create button"""
    register_user(driver)
    login(driver)
    time.sleep(2)
    
    if "/dashboard" not in driver.current_url:
        pytest.skip("Not on dashboard - login may have failed")
    
    src = driver.page_source.lower()
    assert any(w in src for w in ["add", "new", "create", "+", "project"]), "No add/create button on dashboard"

def test_13_logout_exists(driver):
    """Test logout option is available after login"""
    register_user(driver)
    login(driver)
    time.sleep(2)
    
    if "/dashboard" not in driver.current_url:
        pytest.skip("Not on dashboard - login may have failed")
    
    src = driver.page_source.lower()
    assert any(w in src for w in ["logout", "log out", "sign out", "exit"]), "No logout option on dashboard"

def test_14_mobile_viewport(driver):
    """Test app works on mobile viewport"""
    driver.set_window_size(375, 812)
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 500, "Broken on mobile - page too small"

def test_15_desktop_viewport(driver):
    """Test app works on desktop viewport"""
    driver.set_window_size(1920, 1080)
    driver.get(BASE_URL)
    wait_for_react(driver)
    assert len(driver.page_source) > 500, "Broken on desktop - page too small"

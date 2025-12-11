"""
Playwright E2E Tests for Login
Tests both positive and negative scenarios for user login
"""
import pytest
import random


class TestLogin:
    """Test suite for login page E2E tests"""
    
    def test_login_success_with_valid_credentials(self, page, base_url):
        """
        POSITIVE TEST: Login with valid email and password
        Verifies success message and token storage
        """
        # First, register a user
        unique_id = random.randint(10000, 99999)
        test_email = f"loginuser{unique_id}@example.com"
        test_password = "validPassword123"
        
        # Register the user
        page.goto(f"{base_url}/static/register.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        page.click("button[type='submit']")
        page.wait_for_timeout(1000)  # Wait for registration
        
        # Clear localStorage
        page.evaluate("() => localStorage.clear()")
        
        # Now go to login page
        page.goto(f"{base_url}/static/login.html")
        
        # Fill login form
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for redirect to calculations page
        page.wait_for_timeout(2000)
        
        # Should redirect to calculations.html after successful login
        assert "calculations.html" in page.url, f"Expected redirect to calculations.html, got URL: {page.url}"
        
        # Verify JWT token is stored in localStorage
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is not None, "JWT token should be stored in localStorage"
        assert len(token) > 0, "JWT token should not be empty"
    
    def test_login_with_invalid_credentials_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Login with incorrect password
        Should show 401 Unauthorized error
        """
        page.goto(f"{base_url}/static/login.html")
        
        # Try to login with non-existent credentials
        page.fill("#email", "nonexistent@example.com")
        page.fill("#password", "wrongpassword123")
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about invalid credentials (text is present even if element is hidden)
        error_message = page.locator("#error")
        error_text = error_message.text_content().lower()
        assert "invalid" in error_text or "credentials" in error_text or "incorrect" in error_text, f"Expected error message, got: {error_text}"
        
        # Should NOT redirect (stay on login page)
        assert "login.html" in page.url, f"Should stay on login page, got: {page.url}"
        
        # Verify no token stored
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is None
    
    def test_login_with_wrong_password_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Login with correct email but wrong password
        Should show 401 error
        """
        # First register a user
        unique_id = random.randint(10000, 99999)
        test_email = f"wrongpass{unique_id}@example.com"
        test_password = "correctPassword123"
        
        page.goto(f"{base_url}/static/register.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        page.click("button[type='submit']")
        page.wait_for_timeout(1000)
        
        # Now try to login with wrong password
        page.goto(f"{base_url}/static/login.html")
        page.fill("#email", test_email)
        page.fill("#password", "wrongPassword456")
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message
        error_message = page.locator("#error")
        error_text = error_message.text_content().lower()
        assert "invalid" in error_text or "credentials" in error_text, f"Expected error message, got: {error_text}"
        
        # Should NOT redirect
        assert "login.html" in page.url
    
    def test_login_with_invalid_email_format_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Login with invalid email format
        Should show client-side validation error
        """
        page.goto(f"{base_url}/static/login.html")
        
        # Fill form with invalid email
        page.fill("#email", "notanemail")  # No @ symbol
        page.fill("#password", "password123")
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about email format
        error_message = page.locator("#error")
        assert "email" in error_message.text_content().lower()
        
        # Should NOT redirect
        assert "login.html" in page.url
    
    def test_login_with_empty_password_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Login with empty password
        Should show client-side validation error
        """
        page.goto(f"{base_url}/static/login.html")
        
        # Fill only email, leave password empty
        page.fill("#email", "test@example.com")
        # Don't fill password
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about password
        error_message = page.locator("#error")
        assert "password" in error_message.text_content().lower()
        
        # Should NOT redirect
        assert "login.html" in page.url
    
    def test_login_page_elements_present(self, page, base_url):
        """
        POSITIVE TEST: Verify all form elements are present
        """
        page.goto(f"{base_url}/static/login.html")
        
        # Check form elements exist
        assert page.locator("#email").is_visible()
        assert page.locator("#password").is_visible()
        assert page.locator("button[type='submit']").is_visible()
        
        # Check input types
        assert page.locator("#email").get_attribute("type") == "email"
        assert page.locator("#password").get_attribute("type") == "password"
    
    def test_full_workflow_register_then_login(self, page, base_url):
        """
        POSITIVE TEST: Complete workflow - register a new user, then login
        """
        # Generate unique credentials
        unique_id = random.randint(10000, 99999)
        test_email = f"workflow{unique_id}@example.com"
        test_password = "workflowPassword123"
        
        # Step 1: Register
        page.goto(f"{base_url}/static/register.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        page.click("button[type='submit']")
        
        # Wait for registration and redirect
        page.wait_for_timeout(2000)
        
        # Should redirect to calculations after registration
        assert "calculations.html" in page.url
        
        # Clear the token
        page.evaluate("() => localStorage.clear()")
        
        # Step 2: Login with same credentials
        page.goto(f"{base_url}/static/login.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.click("button[type='submit']")
        
        # Wait for login and redirect
        page.wait_for_timeout(2000)
        
        # Should redirect to calculations after login
        assert "calculations.html" in page.url
        
        # Verify token exists
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is not None
        assert len(token) > 0

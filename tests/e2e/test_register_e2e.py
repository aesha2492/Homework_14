"""
Playwright E2E Tests for Registration
Tests both positive and negative scenarios for user registration
"""
import pytest
import re


class TestRegistration:
    """Test suite for registration page E2E tests"""
    
    def test_register_success_with_valid_data(self, page, base_url):
        """
        POSITIVE TEST: Register with valid email and password
        Verifies success message is displayed
        """
        # Navigate to registration page
        page.goto(f"{base_url}/static/register.html")
        
        # Generate unique email for this test
        import random
        unique_id = random.randint(10000, 99999)
        test_email = f"testuser{unique_id}@example.com"
        test_password = "validPassword123"
        
        # Fill in the form
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        
        # Submit the form
        page.click("button[type='submit']")
        
        # Wait for redirect to calculations page
        page.wait_for_timeout(2000)
        
        # Should redirect to calculations.html after successful registration
        assert "calculations.html" in page.url, f"Expected redirect to calculations.html, got URL: {page.url}"
        
        # Verify JWT token is stored in localStorage
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is not None, "JWT token should be stored"
        assert len(token) > 0, "JWT token should not be empty"
    
    def test_register_with_short_password_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Register with password less than 8 characters
        Should show client-side validation error
        """
        page.goto(f"{base_url}/static/register.html")
        
        # Fill form with short password
        page.fill("#email", "test@example.com")
        page.fill("#password", "short")  # Only 5 characters
        page.fill("#confirm-password", "short")
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about password length
        error_message = page.locator("#error")
        assert "8 characters" in error_message.text_content().lower()
        
        # Should NOT redirect
        assert "register.html" in page.url
    
    def test_register_with_mismatched_passwords_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Register with non-matching passwords
        Should show client-side validation error
        """
        page.goto(f"{base_url}/static/register.html")
        
        # Fill form with mismatched passwords
        page.fill("#email", "test@example.com")
        page.fill("#password", "password123")
        page.fill("#confirm-password", "password456")
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about password mismatch
        error_message = page.locator("#error")
        assert "do not match" in error_message.text_content().lower()
        
        # Should NOT redirect
        assert "register.html" in page.url
    
    def test_register_with_invalid_email_shows_error(self, page, base_url):
        """
        NEGATIVE TEST: Register with invalid email format
        Should show client-side validation error
        """
        page.goto(f"{base_url}/static/register.html")
        
        # Fill form with invalid email
        page.fill("#email", "notanemail")  # No @ symbol
        page.fill("#password", "password123")
        page.fill("#confirm-password", "password123")
        
        # Submit form
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about email format
        error_message = page.locator("#error")
        assert "email" in error_message.text_content().lower()
        
        # Should NOT redirect
        assert "register.html" in page.url
    
    def test_register_with_duplicate_email_shows_server_error(self, page, base_url):
        """
        NEGATIVE TEST: Register with already registered email
        Should show server-side error (400)
        """
        # Generate unique email
        import random
        unique_id = random.randint(10000, 99999)
        test_email = f"duplicate{unique_id}@example.com"
        test_password = "password123"
        
        # First registration
        page.goto(f"{base_url}/static/register.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        page.click("button[type='submit']")
        
        # Wait for first registration to complete
        page.wait_for_timeout(1000)
        
        # Try to register again with same email
        page.goto(f"{base_url}/static/register.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        page.click("button[type='submit']")
        
        # Wait for error response
        page.wait_for_timeout(2000)
        
        # Verify error message about duplicate email
        error_message = page.locator("#error")
        error_text = error_message.text_content().lower()
        assert "already" in error_text or "exists" in error_text or "registered" in error_text, f"Expected duplicate error, got: {error_text}"
        
        # Should NOT redirect
        assert "register.html" in page.url
    
    def test_registration_page_elements_present(self, page, base_url):
        """
        POSITIVE TEST: Verify all form elements are present
        """
        page.goto(f"{base_url}/static/register.html")
        
        # Check form elements exist
        assert page.locator("#email").is_visible()
        assert page.locator("#password").is_visible()
        assert page.locator("#confirm-password").is_visible()
        assert page.locator("button[type='submit']").is_visible()
        
        # Check input types
        assert page.locator("#email").get_attribute("type") == "email"
        assert page.locator("#password").get_attribute("type") == "password"
        assert page.locator("#confirm-password").get_attribute("type") == "password"

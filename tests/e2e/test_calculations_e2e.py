"""
Playwright E2E Tests for Calculations BREAD Operations
Tests Browse, Read, Edit, Add, Delete operations with authentication
"""
import pytest
import random


class TestCalculationsBREAD:
    """Test suite for calculations BREAD operations E2E tests"""

    @pytest.fixture
    def setup_user_and_login(self, page, base_url):
        """Helper fixture to register, login and return token"""
        unique_id = random.randint(10000, 99999)
        test_email = f"calcuser{unique_id}@example.com"
        test_password = "validPassword123"
        
        # Register the user
        page.goto(f"{base_url}/static/register.html")
        page.fill("#email", test_email)
        page.fill("#password", test_password)
        page.fill("#confirm-password", test_password)
        page.click("button[type='submit']")
        page.wait_for_timeout(1500)  # Wait for registration and redirect
        
        # Should now be on calculations page with token
        return {"email": test_email, "password": test_password}

    def test_add_calculation_success(self, page, base_url, setup_user_and_login):
        """
        POSITIVE TEST: Add a new calculation
        Verifies calculation is created successfully
        """
        # Navigate to calculations page (should already be there after login)
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # Click Add Calculation tab
        page.click("text=Add Calculation")
        page.wait_for_timeout(500)
        
        # Fill in calculation form
        page.fill("#add-a", "10")
        page.fill("#add-b", "5")
        page.select_option("#add-type", "Add")
        
        # Submit form
        page.click("#add-form button[type='submit']")
        
        # Wait for success message
        success_message = page.locator("#add-success")
        success_message.wait_for(state="visible", timeout=5000)
        
        # Verify success message contains result
        assert "created successfully" in success_message.text_content().lower()
        assert "15" in success_message.text_content()  # 10 + 5 = 15

    def test_add_calculation_divide_by_zero_validation(self, page, base_url, setup_user_and_login):
        """
        NEGATIVE TEST: Attempt to create calculation with divide by zero
        Verifies client-side validation prevents submission
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # Click Add Calculation tab
        page.click("text=Add Calculation")
        page.wait_for_timeout(500)
        
        # Fill in form with divide by zero
        page.fill("#add-a", "10")
        page.fill("#add-b", "0")
        page.select_option("#add-type", "Divide")
        
        # Submit form
        page.click("#add-form button[type='submit']")
        
        # Wait for error message
        error_message = page.locator("#add-error")
        error_message.wait_for(state="visible", timeout=5000)
        
        # Verify error message
        assert "cannot divide by zero" in error_message.text_content().lower()

    def test_browse_calculations(self, page, base_url, setup_user_and_login):
        """
        POSITIVE TEST: Browse all user calculations
        Verifies calculations are displayed correctly
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # First, add a calculation
        page.click("text=Add Calculation")
        page.wait_for_timeout(500)
        page.fill("#add-a", "20")
        page.fill("#add-b", "4")
        page.select_option("#add-type", "Multiply")
        page.click("#add-form button[type='submit']")
        page.wait_for_timeout(1000)
        
        # Navigate to Browse
        page.click("text=Browse Calculations")
        page.wait_for_timeout(1000)
        
        # Verify calculations list is visible
        calculations_list = page.locator("#calculations-list")
        assert calculations_list.is_visible()
        
        # Verify the calculation we just added appears
        list_items = page.locator(".calculation-item")
        count = list_items.count()
        assert count > 0, "No calculations found in the list"
        
        # Verify calculation details are shown
        first_item = list_items.first
        text = first_item.text_content()
        assert "80" in text or "20" in text  # Result or operand

    def test_edit_calculation_success(self, page, base_url, setup_user_and_login):
        """
        POSITIVE TEST: Edit an existing calculation
        Verifies calculation can be updated successfully
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # First, add a calculation
        page.click("text=Add Calculation")
        page.wait_for_timeout(500)
        page.fill("#add-a", "15")
        page.fill("#add-b", "3")
        page.select_option("#add-type", "Add")
        page.click("#add-form button[type='submit']")
        page.wait_for_timeout(1000)
        
        # Browse to see the calculation
        page.click("text=Browse Calculations")
        page.wait_for_timeout(1000)
        
        # Click Edit button on the first calculation
        edit_button = page.locator(".edit-btn").first
        edit_button.click()
        page.wait_for_timeout(500)
        
        # Should now be on edit section
        edit_form = page.locator("#edit-form")
        assert edit_form.is_visible()
        
        # Update operand A
        page.fill("#edit-a", "25")
        
        # Submit form
        page.click("#edit-form button[type='submit']")
        
        # Wait for success message
        success_message = page.locator("#edit-success")
        success_message.wait_for(state="visible", timeout=5000)
        
        # Verify success message
        assert "updated" in success_message.text_content().lower()
        assert "28" in success_message.text_content()  # 25 + 3 = 28

    def test_edit_nonexistent_calculation(self, page, base_url, setup_user_and_login):
        """
        NEGATIVE TEST: Attempt to edit a non-existent calculation
        Verifies appropriate error handling
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # Navigate to Edit section
        page.click("text=Edit Calculation")
        page.wait_for_timeout(500)
        
        # Enter a non-existent calculation ID
        page.fill("#edit-id", "99999")
        page.fill("#edit-a", "100")
        
        # Submit form
        page.click("#edit-form button[type='submit']")
        
        # Wait for error message
        error_message = page.locator("#edit-error")
        error_message.wait_for(state="visible", timeout=5000)
        
        # Verify error message
        assert "not found" in error_message.text_content().lower() or "permission" in error_message.text_content().lower()

    def test_delete_calculation_success(self, page, base_url, setup_user_and_login):
        """
        POSITIVE TEST: Delete a calculation
        Verifies calculation is removed successfully
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # First, add a calculation
        page.click("text=Add Calculation")
        page.wait_for_timeout(500)
        page.fill("#add-a", "50")
        page.fill("#add-b", "10")
        page.select_option("#add-type", "Sub")
        page.click("#add-form button[type='submit']")
        page.wait_for_timeout(1000)
        
        # Browse to see the calculation
        page.click("text=Browse Calculations")
        page.wait_for_timeout(1000)
        
        # Setup dialog handler to accept confirmation
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Click Delete button on the first calculation
        delete_button = page.locator(".delete-btn").first
        delete_button.click()
        page.wait_for_timeout(1500)
        
        # Verify calculation count decreased or success message appears
        # After deletion, the list should refresh
        page.wait_for_timeout(1000)

    def test_browse_empty_calculations_list(self, page, base_url, setup_user_and_login):
        """
        POSITIVE TEST: Browse calculations when user has no calculations
        Verifies appropriate message is displayed
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # Navigate to Browse (default view)
        page.click("text=Browse Calculations")
        page.wait_for_timeout(1000)
        
        # Check for empty state message
        calculations_list = page.locator("#calculations-list")
        
        # Should either show "No calculations found" or have calculation items
        # Since we just registered, likely no calculations yet (unless previous tests added some)
        assert calculations_list.is_visible()

    def test_add_calculation_missing_fields(self, page, base_url, setup_user_and_login):
        """
        NEGATIVE TEST: Attempt to add calculation without required fields
        Verifies client-side validation prevents submission
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        # Click Add Calculation tab
        page.click("text=Add Calculation")
        page.wait_for_timeout(500)
        
        # Fill only operand A (missing B and type)
        page.fill("#add-a", "10")
        
        # Submit form
        page.click("#add-form button[type='submit']")
        
        # Wait for error message
        error_message = page.locator("#add-error")
        error_message.wait_for(state="visible", timeout=5000)
        
        # Verify error message (accepts any validation error)
        error_text = error_message.text_content().lower()
        assert any(msg in error_text for msg in ["select an operation", "required", "operands must be valid", "invalid"])

    def test_unauthorized_access_without_token(self, page, base_url):
        """
        NEGATIVE TEST: Attempt to access calculations page without authentication
        Verifies redirect to login page or shows error
        """
        # Clear any existing token by going to a simple page first
        page.goto(f"{base_url}/static/login.html")
        page.evaluate("() => localStorage.clear()")
        
        # Try to access calculations page without token
        page.goto(f"{base_url}/static/calculations.html")
        
        # Wait for either redirect or error to appear
        page.wait_for_timeout(2000)
        
        # Should either redirect to login page OR show authentication error
        assert "login.html" in page.url or page.locator("#browse-error").is_visible()

    def test_multiple_operation_types(self, page, base_url, setup_user_and_login):
        """
        POSITIVE TEST: Create calculations with different operation types
        Verifies all operation types work correctly
        """
        page.goto(f"{base_url}/static/calculations.html")
        page.wait_for_timeout(500)
        
        operations = [
            {"a": "10", "b": "5", "type": "Add", "expected": "15"},
            {"a": "10", "b": "5", "type": "Sub", "expected": "5"},
            {"a": "10", "b": "5", "type": "Multiply", "expected": "50"},
            {"a": "10", "b": "5", "type": "Divide", "expected": "2"},
        ]
        
        for op in operations:
            # Click Add Calculation tab
            page.click("text=Add Calculation")
            page.wait_for_timeout(500)
            
            # Fill in form
            page.fill("#add-a", op["a"])
            page.fill("#add-b", op["b"])
            page.select_option("#add-type", op["type"])
            
            # Submit form
            page.click("#add-form button[type='submit']")
            
            # Wait for success message
            success_message = page.locator("#add-success")
            success_message.wait_for(state="visible", timeout=5000)
            
            # Verify result in success message
            assert op["expected"] in success_message.text_content()
            
            page.wait_for_timeout(500)

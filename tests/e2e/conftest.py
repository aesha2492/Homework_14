import pytest
import subprocess
import time
import os
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def server(base_url):
    """
    Start the FastAPI server for E2E tests.
    Skip if server is already running (e.g., in CI or manual testing).
    """
    # Check if server is already running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        # Server already running
        print("Server already running at", base_url)
        yield
        return
    
    # Start server
    print("Starting FastAPI server...")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    max_retries = 30
    for _ in range(max_retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            print("Server started successfully")
            break
        time.sleep(0.5)
    else:
        process.kill()
        raise RuntimeError("Failed to start server")
    
    yield
    
    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="function")
def browser_context(server, base_url):
    """Create a browser context for each test"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(base_url=base_url)
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Create a new page for each test"""
    page = browser_context.new_page()
    yield page
    page.close()

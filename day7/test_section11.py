#!/usr/bin/env python3
"""
Section 11 Testing Script
Tests authentication, user-scoped endpoints, and admin routes.

Run this script to verify your Section 11 implementation.
Make sure your FastAPI server is running: uvicorn main:app --reload
"""

import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(test_name: str):
    print(f"\n{Colors.BLUE}=== {test_name} ==={Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}→ {message}{Colors.RESET}")

# Test data
ADMIN_USER = {
    "username": "admin_user",
    "email": "admin@test.com",
    "first_name": "Admin",
    "last_name": "User",
    "password": "admin123",
    "role": "admin"
}

REGULAR_USER = {
    "username": "regular_user",
    "email": "regular@test.com",
    "first_name": "Regular",
    "last_name": "User",
    "password": "user123",
    "role": "user"
}

ANOTHER_USER = {
    "username": "another_user",
    "email": "another@test.com",
    "first_name": "Another",
    "last_name": "User",
    "password": "user456",
    "role": "user"
}

# Global storage for tokens and IDs
tokens: Dict[str, str] = {}
user_ids: Dict[str, int] = {}
todo_ids: Dict[str, int] = {}

def test_create_user(user_data: dict, user_key: str) -> bool:
    """Test user creation"""
    print_info(f"Creating user: {user_data['username']}")
    response = requests.post(f"{BASE_URL}/auth/", json=user_data)
    
    if response.status_code == 201:
        print_success(f"User {user_data['username']} created")
        return True
    elif response.status_code == 400:
        print_error(f"User {user_data['username']} might already exist")
        return False
    else:
        print_error(f"Failed to create user: {response.status_code} - {response.text}")
        return False

def test_login(username: str, password: str, user_key: str) -> bool:
    """Test user login and token retrieval"""
    print_info(f"Logging in as {username}")
    form_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/token", data=form_data)
    
    if response.status_code == 200:
        data = response.json()
        tokens[user_key] = data["access_token"]
        print_success(f"Login successful, token received")
        print_info(f"Token: {tokens[user_key][:50]}...")
        return True
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return False

def get_auth_headers(user_key: str) -> dict:
    """Get authorization headers for a user"""
    if user_key not in tokens:
        return {}
    return {"Authorization": f"Bearer {tokens[user_key]}"}

def test_create_todo(user_key: str, todo_data: dict) -> Optional[int]:
    """Test creating a todo"""
    print_info(f"Creating todo: {todo_data['title']}")
    response = requests.post(
        f"{BASE_URL}/todo/",
        json=todo_data,
        headers=get_auth_headers(user_key)
    )
    
    if response.status_code == 201:
        print_success(f"Todo created successfully")
        # Get the created todo ID by fetching all todos
        todos = test_get_all_todos(user_key)
        if todos:
            # Find the todo we just created (by title)
            for todo in todos:
                if todo.get("title") == todo_data["title"]:
                    todo_id = todo.get("id")
                    todo_ids[user_key] = todo_id
                    print_info(f"Created todo ID: {todo_id}")
                    return todo_id
        return None
    else:
        print_error(f"Failed to create todo: {response.status_code} - {response.text}")
        return None

def test_get_all_todos(user_key: str) -> list:
    """Test getting all todos for a user"""
    print_info(f"Fetching all todos for {user_key}")
    response = requests.get(
        f"{BASE_URL}/todo/",
        headers=get_auth_headers(user_key)
    )
    
    if response.status_code == 200:
        todos = response.json()
        print_success(f"Retrieved {len(todos)} todos")
        return todos
    else:
        print_error(f"Failed to get todos: {response.status_code} - {response.text}")
        return []

def test_admin_get_all_todos() -> bool:
    """Test admin endpoint to get all todos"""
    print_info("Testing admin GET /admin/todo endpoint")
    response = requests.get(
        f"{BASE_URL}/admin/todo",
        headers=get_auth_headers("admin")
    )
    
    if response.status_code == 200:
        todos = response.json()
        print_success(f"Admin retrieved {len(todos)} todos (all users)")
        return True
    elif response.status_code == 401:
        print_error("Admin endpoint returned 401 - check role in token")
        return False
    else:
        print_error(f"Admin endpoint failed: {response.status_code} - {response.text}")
        return False

def test_regular_user_admin_access() -> bool:
    """Test that regular user cannot access admin endpoints"""
    print_info("Testing regular user trying to access admin endpoint")
    response = requests.get(
        f"{BASE_URL}/admin/todo",
        headers=get_auth_headers("regular")
    )
    
    if response.status_code == 401:
        print_success("Regular user correctly blocked from admin endpoint")
        return True
    else:
        print_error(f"Security issue: Regular user accessed admin endpoint! Status: {response.status_code}")
        return False

def test_admin_delete_todo(todo_id: int) -> bool:
    """Test admin deleting any todo"""
    print_info(f"Testing admin delete of todo ID: {todo_id}")
    response = requests.delete(
        f"{BASE_URL}/admin/{todo_id}",
        headers=get_auth_headers("admin")
    )
    
    if response.status_code == 204:
        print_success(f"Admin successfully deleted todo {todo_id}")
        return True
    elif response.status_code == 401:
        print_error("Admin delete returned 401 - check role in token")
        return False
    elif response.status_code == 404:
        print_error(f"Todo {todo_id} not found")
        return False
    else:
        print_error(f"Admin delete failed: {response.status_code} - {response.text}")
        return False

def test_user_cannot_access_other_user_todo() -> bool:
    """Test that user cannot access another user's todo"""
    print_info("Testing user isolation - user should only see their own todos")
    
    # Get todos for regular user
    regular_todos = test_get_all_todos("regular")
    another_todos = test_get_all_todos("another")
    
    if len(regular_todos) > 0 and len(another_todos) > 0:
        regular_todo_id = regular_todos[0]["id"]
        another_todo_id = another_todos[0]["id"]
        
        # Try to access another user's todo
        print_info(f"Regular user trying to access another user's todo ID: {another_todo_id}")
        response = requests.get(
            f"{BASE_URL}/todo/{another_todo_id}",
            headers=get_auth_headers("regular")
        )
        
        if response.status_code == 404:
            print_success("User correctly cannot access another user's todo")
            return True
        else:
            print_error(f"Security issue: User accessed another user's todo! Status: {response.status_code}")
            return False
    else:
        print_info("Skipping - need todos from both users")
        return True

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Section 11 Testing Suite")
    print("="*60 + Colors.RESET)
    print("\nMake sure your FastAPI server is running:")
    print("  cd /Users/akashthakur/Documents/code/My-learning/01-career/learning/fastapi/day7")
    print("  pyenv activate lastapi-learning")
    print("  uvicorn main:app --reload")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        print_success("Server is running, starting tests...\n")
    except requests.exceptions.RequestException:
        print_error("Cannot connect to server. Please start it first.")
        return
    
    results = []
    
    # ========== TEST 1: Create Users ==========
    print_test("TEST 1: User Creation")
    results.append(("Create Admin User", test_create_user(ADMIN_USER, "admin")))
    results.append(("Create Regular User", test_create_user(REGULAR_USER, "regular")))
    results.append(("Create Another User", test_create_user(ANOTHER_USER, "another")))
    
    # ========== TEST 2: User Login ==========
    print_test("TEST 2: User Authentication")
    results.append(("Admin Login", test_login(ADMIN_USER["username"], ADMIN_USER["password"], "admin")))
    results.append(("Regular User Login", test_login(REGULAR_USER["username"], REGULAR_USER["password"], "regular")))
    results.append(("Another User Login", test_login(ANOTHER_USER["username"], ANOTHER_USER["password"], "another")))
    
    # ========== TEST 3: Create Todos ==========
    print_test("TEST 3: Create Todos (User-Scoped)")
    todo1 = {"title": "Admin's First Todo", "description": "This is admin's todo", "priority": 1, "complete": False}
    todo2 = {"title": "Regular User's Todo", "description": "This is regular user's todo", "priority": 2, "complete": False}
    todo3 = {"title": "Another User's Todo", "description": "This is another user's todo", "priority": 3, "complete": False}
    
    results.append(("Create Admin Todo", test_create_todo("admin", todo1) is not None))
    results.append(("Create Regular User Todo", test_create_todo("regular", todo2) is not None))
    results.append(("Create Another User Todo", test_create_todo("another", todo3) is not None))
    
    # ========== TEST 4: User-Scoped Access ==========
    print_test("TEST 4: User-Scoped Endpoints")
    admin_todos = test_get_all_todos("admin")
    regular_todos = test_get_all_todos("regular")
    another_todos = test_get_all_todos("another")
    
    results.append(("Admin sees only their todos", len(admin_todos) == 1))
    results.append(("Regular user sees only their todos", len(regular_todos) == 1))
    results.append(("Another user sees only their todos", len(another_todos) == 1))
    
    # ========== TEST 5: Admin Endpoints ==========
    print_test("TEST 5: Admin Endpoints")
    results.append(("Admin can see all todos", test_admin_get_all_todos()))
    results.append(("Regular user blocked from admin endpoint", test_regular_user_admin_access()))
    
    # ========== TEST 6: User Isolation ==========
    print_test("TEST 6: User Isolation (Security)")
    results.append(("User cannot access other user's todos", test_user_cannot_access_other_user_todo()))
    
    # ========== TEST 7: Admin Delete ==========
    print_test("TEST 7: Admin Delete Capability")
    if "regular" in todo_ids:
        results.append(("Admin can delete any user's todo", test_admin_delete_todo(todo_ids["regular"])))
    
    # ========== SUMMARY ==========
    print_test("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.RESET}\n")
    
    for test_name, result in results:
        if result:
            print_success(test_name)
        else:
            print_error(test_name)
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 All tests passed! Section 11 is solid!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Review the errors above.{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Make sure uvicorn is running on http://localhost:8000")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


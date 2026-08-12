# API Tests

This directory contains pytest-based tests for the Mergington High School Activities API.

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run tests with verbose output
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_signup.py
```

### Run specific test class or function
```bash
pytest tests/test_signup.py::TestSignupForActivity::test_signup_success_with_valid_activity_and_email
```

### Run tests and generate coverage report
```bash
pytest tests/ --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html` showing which lines are covered by tests.

## Test Structure

### Files
- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_activities.py`** - Tests for GET /activities endpoint
- **`test_signup.py`** - Tests for POST /activities/{activity_name}/signup endpoint
- **`test_unregister.py`** - Tests for DELETE /activities/{activity_name}/unregister endpoint

## Fixtures

Fixtures are reusable test utilities defined in `conftest.py`:

### `test_client`
Provides a FastAPI `TestClient` for making HTTP requests to the app.

```python
def test_example(test_client):
    response = test_client.get("/activities")
    assert response.status_code == 200
```

### `mock_activities`
Replaces the app's activities dictionary with fresh test data for each test, ensuring:
- No test pollution (one test's changes don't affect others)
- Consistent starting state (all tests start with initial activities)
- Reliable, repeatable results

Uses `monkeypatch` to inject isolated test data.

```python
def test_example(test_client, mock_activities):
    # mock_activities is a fresh copy, modifications won't affect other tests
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@example.com"}
    )
```

### `fresh_activities`
Returns a deep copy of the activities dictionary. Use this if you need the data without monkeypatching.

### `test_emails`
Provides common test email addresses:
- `new_student` - An email not registered for any activity
- `existing_student` - michael@mergington.edu (already in Chess Club)
- `another_student` - Another unregistered email

```python
def test_example(test_client, test_emails):
    email = test_emails["new_student"]
```

### `test_activities_names`
Provides test activity names:
- `valid` - "Chess Club" (exists in test data)
- `invalid` - "Nonexistent Club" (does not exist)

```python
def test_example(test_client, test_activities_names):
    response = test_client.post(
        f"/activities/{test_activities_names['valid']}/signup",
        params={"email": "test@example.com"}
    )
```

## Test Coverage

Current test coverage targets core API endpoints:

| Endpoint | Tests | Coverage |
|----------|-------|----------|
| GET /activities | 5 | Structure, data integrity, edge cases |
| POST /signup | 8 | Success, validation, error cases, isolation |
| DELETE /unregister | 8 | Success, validation, error cases, data integrity |

Coverage target: **>80% of src/app.py**

Run `pytest tests/ --cov=src --cov-report=term-missing` to see detailed coverage per line.

## Adding New Tests

### Example: Testing a new error case

```python
# In tests/test_signup.py
def test_signup_with_special_characters_in_email(self, test_client, mock_activities):
    """Test that special characters in email are handled."""
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": "test+tag@example.com"}
    )
    # Assert expected behavior
    assert response.status_code == 200  # or 400, depending on requirements
```

### Tips
1. Always use the `mock_activities` fixture to ensure test isolation
2. Include descriptive docstrings explaining what the test validates
3. Use `test_emails` and `test_activities_names` fixtures for common values
4. Assert both status code and response data structure
5. Group related tests in classes (e.g., `TestSignupForActivity`)

## Continuous Integration

Tests can be integrated into GitHub Actions or other CI systems:

```yaml
- name: Run tests
  run: pytest tests/ --cov=src --cov-report=xml

- name: Check coverage threshold
  run: pytest tests/ --cov=src --cov-fail-under=80
```

## Troubleshooting

### "No module named 'src'"
Ensure `pytest.ini` contains `pythonpath = .` and you're running pytest from the workspace root.

### Tests pass locally but fail in CI
Check that pytest-cov is in `requirements.txt` and installed in CI environment.

### Test isolation issues
Ensure all tests use the `mock_activities` fixture. If a test uses raw `activities` dict, it may pollute other tests.

## Resources

- [Pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [TestClient documentation](https://fastapi.tiangolo.com/reference/testclient/)

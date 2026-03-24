#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Test '123'
print("Testing password '123':")
try:
    validate_password('123')
    print("  -> ACCEPTED (SHOULD FAIL!)")
except ValidationError as e:
    print(f"  -> REJECTED: {e.messages}")

# Test 'SecurePass123!'
print("\nTesting password 'SecurePass123!':")
try:
    validate_password('SecurePass123!')
    print("  -> ACCEPTED (CORRECT)")
except ValidationError as e:
    print(f"  -> REJECTED: {e.messages}")

# Test with custom validator
print("\n" + "="*50)
print("Testing RegisterSerializer with '123':")
from users.serializers import RegisterSerializer

data = {
    'email': 'test@test.com',
    'username': 'testuser',
    'password': '123',
    'password2': '123',
    'role': 'student'
}

s = RegisterSerializer(data=data)
is_valid = s.is_valid()
print(f"  is_valid(): {is_valid}")
if not is_valid:
    print(f"  errors: {s.errors}")
else:
    print("  -> ACCEPTED (SHOULD FAIL!)")

"""Test script to debug import issues."""
print("1. Starting imports...")

try:
    print("2. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("3. Importing src.api...")
    from src import api
    print("   ✓ src.api imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("4. Importing routes...")
    from src.api import routes
    print("   ✓ routes imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n✓ All imports successful!")

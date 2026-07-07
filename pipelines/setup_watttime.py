#!/usr/bin/env python3
"""
Setup WattTime credentials using cross-platform keyring
Falls back to environment variables for CI/CD deployments
"""
import keyring
import getpass
import sys

SERVICE_NAME = "esg-carbon-tracker-watttime"

def setup_credentials():
    print("=== WattTime Credentials Setup ===\n")

    # Check if already configured
    existing_username = keyring.get_password(SERVICE_NAME, "username")
    if existing_username:
        print(f"Credentials already exist for: {existing_username}")
        response = input("Update credentials? (y/N): ").strip().lower()
        if response != 'y':
            print("Keeping existing credentials")
            return

    # Get credentials
    print("\nEnter your WattTime credentials:")
    username = input("Username/Email: ").strip()
    password = getpass.getpass("Password: ")

    if not username or not password:
        print("✗ Username and password are required")
        sys.exit(1)

    # Store in keyring
    try:
        keyring.set_password(SERVICE_NAME, "username", username)
        keyring.set_password(SERVICE_NAME, "password", password)
        print(f"\n✓ Credentials stored in system keyring")
        print(f"  Service: {SERVICE_NAME}")
        print(f"  Username: {username}")

        print("\nCredentials will be used automatically by:")
        print("  - test_watttime.py")
        print("  - load_watttime_data.py")
        print("  - WattTime pipeline")

    except Exception as e:
        print(f"\n✗ Failed to store credentials: {e}")
        print("\nFallback: Set environment variables instead:")
        print(f"  export WATTTIME_USERNAME='{username}'")
        print(f"  export WATTTIME_PASSWORD='YOUR_PASSWORD'")
        sys.exit(1)

def show_credentials():
    """Show stored credentials (password masked)"""
    username = keyring.get_password(SERVICE_NAME, "username")
    if username:
        print(f"Stored username: {username}")
        print("Password: ********")
    else:
        print("No credentials stored in keyring")

def delete_credentials():
    """Delete stored credentials"""
    try:
        keyring.delete_password(SERVICE_NAME, "username")
        keyring.delete_password(SERVICE_NAME, "password")
        print("✓ Credentials deleted")
    except keyring.errors.PasswordDeleteError:
        print("No credentials to delete")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage WattTime credentials")
    parser.add_argument("action", nargs="?", default="setup",
                       choices=["setup", "show", "delete"],
                       help="Action to perform")
    args = parser.parse_args()

    if args.action == "setup":
        setup_credentials()
    elif args.action == "show":
        show_credentials()
    elif args.action == "delete":
        delete_credentials()

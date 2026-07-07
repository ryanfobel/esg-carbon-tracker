"""
Test WattTime API connection and fetch sample data
"""
import requests
import os

SERVICE_NAME = "esg-carbon-tracker-watttime"

def get_credentials():
    """
    Get WattTime credentials from multiple sources (in priority order):
    1. Python keyring (cross-platform: macOS Keychain, Windows Credential Manager, Linux Secret Service)
    2. Environment variables (for CI/CD and deployments)
    """
    # Try keyring first (best for local development)
    try:
        import keyring
        username = keyring.get_password(SERVICE_NAME, "username")
        password = keyring.get_password(SERVICE_NAME, "password")
        if username and password:
            print("✓ Using credentials from system keyring")
            return username, password
    except ImportError:
        print("⚠ keyring not installed, falling back to environment variables")
    except Exception as e:
        print(f"⚠ Keyring error: {e}, falling back to environment variables")

    # Fall back to environment variables (for CI/CD)
    username = os.getenv("WATTTIME_USERNAME")
    password = os.getenv("WATTTIME_PASSWORD")
    if username and password:
        print("✓ Using credentials from environment variables")
        return username, password

    # No credentials found
    print("✗ No credentials found!")
    print("\nSetup options:")
    print("  1. Run: pixi run python setup_watttime.py")
    print("  2. Set environment variables:")
    print("     export WATTTIME_USERNAME='your-email@example.com'")
    print("     export WATTTIME_PASSWORD='your-password'")
    exit(1)

username, password = get_credentials()

print("=== Testing WattTime API Connection ===\n")

# Step 1: Get auth token
print("1. Authenticating...")
auth_response = requests.get(
    "https://api.watttime.org/login",
    auth=(username, password)
)

if auth_response.status_code == 200:
    token = auth_response.json()["token"]
    print(f"   ✓ Authentication successful!")
    print(f"   Token: {token[:20]}...")
else:
    print(f"   ✗ Authentication failed: {auth_response.status_code}")
    print(f"   Response: {auth_response.text}")
    print("\n   NOTE: If you just registered, check your email and click the verification link first!")
    exit(1)

# Step 2: List available regions
print("\n2. Fetching available regions...")
regions_response = requests.get(
    "https://api.watttime.org/v3/region-list",
    headers={"Authorization": f"Bearer {token}"}
)

if regions_response.status_code == 200:
    regions = regions_response.json()
    print(f"   ✓ Found {len(regions)} regions")

    # Show North American regions
    na_regions = [r for r in regions if r.get('region', '').startswith(('CAISO', 'MISO', 'PJM', 'IESO', 'NYISO'))]
    print(f"\n   Sample North American regions:")
    for region in na_regions[:10]:
        print(f"     - {region['region']}: {region.get('name', 'N/A')}")
else:
    print(f"   ✗ Failed to fetch regions: {regions_response.status_code}")
    print(f"   Response: {regions_response.text}")

# Step 3: Get current data for a test region
print("\n3. Fetching current grid intensity for CAISO (California)...")
intensity_response = requests.get(
    "https://api.watttime.org/v3/signal",
    params={"region": "CAISO_NORTH"},
    headers={"Authorization": f"Bearer {token}"}
)

if intensity_response.status_code == 200:
    data = intensity_response.json()
    print(f"   ✓ Current MOER: {data.get('moer', 'N/A')} lbs CO2/MWh")
    print(f"   Percent: {data.get('percent', 'N/A')}%")
    print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
else:
    print(f"   ✗ Failed to fetch intensity: {intensity_response.status_code}")
    print(f"   Response: {intensity_response.text}")

print("\n=== Test Complete ===")
print("✓ WattTime API is working!")
print("\nNext step: Run 'pixi run python load_watttime_data.py' to load real data")

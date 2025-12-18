
import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://127.0.0.1:8080/api/v1"
RELAY_ENDPOINT = f"{BASE_URL}/stacks/relay"
RELAYERS_ENDPOINT = f"{BASE_URL}/relayers"

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def log(type, message):
    if type == "INFO":
        print(f"[{GREEN}INFO{RESET}] {message}")
    elif type == "WARN":
        print(f"[{YELLOW}WARN{RESET}] {message}")
    elif type == "FAIL":
        print(f"[{RED}FAIL{RESET}] {message}")
    elif type == "PASS":
        print(f"[{GREEN}PASS{RESET}] {message}")

def check_connectivity():
    try:
        urllib.request.urlopen("http://127.0.0.1:8080", timeout=1)
        return True # If it returns 200 or 404 but connects, it's basically up (urlopen throws on error though)
    except urllib.error.HTTPError:
        return True
    except urllib.error.URLError:
        return False

def send_request(url, method="GET", headers={}, data=None):
    try:
        req = urllib.request.Request(url, method=method, headers=headers)
        if data:
            req.data = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req) as response:
            return response.getcode(), response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)

def test_auth_headers():
    log("INFO", "Testing Authentication Bypass (Missing Headers)...")
    code, _ = send_request(RELAYERS_ENDPOINT)
    if code in [401, 403]:
        log("PASS", f"Protected endpoint rejected unauthenticated request. Status: {code}")
    elif code == 200:
        log("FAIL", "Protected endpoint allowed unauthenticated request! VULNERABILITY DETECTED.")
    else:
        log("WARN", f"Unexpected status code: {code}")

def test_fuzzing_relay_endpoint(api_key):
    log("INFO", "Fuzzing /relay endpoint (Input Validation)...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 1. Empty Payload
    code, _ = send_request(RELAY_ENDPOINT, method="POST", headers=headers, data={})
    if code in [400, 422]:
        log("PASS", "Empty payload rejected/handled gracefully.")
    else:
        log("FAIL", f"Empty payload return status: {code}")

    # 2. Malformed Hex
    code, text = send_request(RELAY_ENDPOINT, method="POST", headers=headers, data={"tx_hex": "NOT_A_HEX_STRING"})
    if "error" in text.lower() or code != 200:
        log("PASS", "Malformed hex rejected.")
    else:
        log("FAIL", "Malformed hex appeared to be accepted.")

    # 3. Buffer Overflow
    huge_payload = "A" * 1000000
    code, _ = send_request(RELAY_ENDPOINT, method="POST", headers=headers, data={"tx_hex": huge_payload})
    if code in [413, 400, 500]:
        log("PASS", f"Large payload handled. Status: {code}")
    else:
        log("WARN", f"Large payload returned status: {code}")
        
    # 4. SQL Injection Simulated
    code, _ = send_request(RELAY_ENDPOINT, method="POST", headers=headers, data={"tx_hex": "' OR 1=1; --"})
    if code != 200:
        log("PASS", "Injection payload rejected.")
        
    # 5. Serialization Probe
    random_bytes = bytearray([0x00, 0x01, 0xFF, 0xFE] * 100).hex()
    code, _ = send_request(RELAY_ENDPOINT, method="POST", headers=headers, data={"tx_hex": random_bytes})
    if code != 200:
        log("PASS", "Corrupted serialization rejected.")

def main():
    print(f"{YELLOW}Starting Black-box Security Audit...{RESET}")
    print("========================================")
    
    print("Waiting for target server to come online...", end="", flush=True)
    for _ in range(15): # 30 seconds wait total
        if check_connectivity():
            print(" ONLINE!")
            break
        time.sleep(2)
        print(".", end="", flush=True)
    else:
        print("\n")
        log("FAIL", "Target is DOWN. Timed out waiting for server.")
        return

    api_key = "dGVzdC1pcy1hLXJlYWxseS1sb25nLWtleS10aGF0LWlzLXZhbGlk" # For this simulated test, we use the one exported in the run command
    test_auth_headers()
    test_fuzzing_relay_endpoint(api_key)
    
    print("\n========================================")
    print(f"{YELLOW}Audit Complete.{RESET}")

if __name__ == "__main__":
    main()

import msal
import requests
import time
import pprint

# Parameters section
CLIENT_ID = "61f36f8a-52a6-4762-ab4b-c31a6b8c438d"
TENANT_ID = "b6024987-88e6-4e43-b5b6-676c81d30279"




def get_access_token_interactive():

    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    redirect_uri = "http://localhost"


    # Acquire a token for Fabric APIs
    scopes = [
        "https://api.fabric.microsoft.com/Workspace.ReadWrite.All",
        "https://api.fabric.microsoft.com/Item.ReadWrite.All",
        "https://api.fabric.microsoft.com/Tenant.ReadWrite.All"
    ]

    # Create a Public Client Application
    public_client_app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=authority
    )

    # Acquire token interactively without explicitly setting the redirect_uri here
    result = public_client_app.acquire_token_interactive(
        scopes=scopes
    )

    return result["access_token"]





def list_all_workspaces(access_token):
    power_bi_api_endpoint = 'https://api.powerbi.com/v1.0/myorg/groups'  # Endpoint to list all workspaces
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(power_bi_api_endpoint, headers=headers)

    if response.status_code == 200:
        workspaces = response.json().get('value', [])
        if workspaces:
            print("List of Workspaces:")
            for workspace in workspaces:
                print(f"- {workspace['name']} (ID: {workspace['id']})")
        else:
            print("No workspaces found.")
    else:
        print(f"Failed to retrieve workspaces. Status Code: {response.status_code} - {response.text}")




def start_scan_and_get_scan_id(access_token, workspace_list):
    power_bi_api_endpoint = 'https://api.powerbi.com/v1.0/myorg/admin/workspaces/getInfo?lineage=True&datasourceDetails=True&datasetSchema=True&datasetExpressions=True'
    body = {
    "workspaces": workspace_list
    }
    headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    response = requests.post(power_bi_api_endpoint, headers=headers, json=body)
    print("Response:", response.json())
    return response.json()['id']

def get_scan_status(access_token, scan_id):
    power_bi_api_endpoint = f'https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanStatus/{scan_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(power_bi_api_endpoint, headers=headers)
    return response.json()

def get_scan_result(access_token, scan_id):
    power_bi_api_endpoint = f'https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanResult/{scan_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(power_bi_api_endpoint, headers=headers)
    return response.json()

# Get access token (interactive with user context --> needs Fabric admin permissions!)
access_token = get_access_token_interactive()

# List all workspaces to get IDs
list_all_workspaces(access_token)

# Pick one or several to scan (manually enter an ID from the list returned above)
workspaces_to_scan = ["6f54fede-d2b3-466d-be87-ebd54790a40e"]

# start the scan
scan_id = start_scan_and_get_scan_id(access_token, workspaces_to_scan)

# Get scan result
time.sleep(1)
scan_status = get_scan_status(access_token, scan_id)["status"]
if scan_status == "Succeeded":
    scan_result = get_scan_result(access_token, scan_id)
    pprint.pprint(scan_result)
else:
    print("not ready yet, try getting scan result a bit later")





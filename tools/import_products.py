import requests
import os
import sys

BASE_URL = "http://localhost:9000"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3Rvcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMiLCJhY3Rvcl90eXBlIjoidXNlciIsImF1dGhfaWRlbnRpdHlfaWQiOiJhdXRoaWRfMDFLQ0JIOU5RUTkzNEVNR1RaMzdTODIxRkoiLCJhcHBfbWV0YWRhdGEiOnsidXNlcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMifSwidXNlcl9tZXRhZGF0YSI6e30sImlhdCI6MTc2NTYzODkxNSwiZXhwIjoxNzY1NzI1MzE1fQ.czxdeobiXTKYXiS2QRsmsfwtOiF3Q-rJqPUTDDLW68Y"

HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
}

def import_products(file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    print(f"Step 1: Getting presigned URL for {file_name}...")
    # 1. Get presigned URL
    # In Medusa v2, the endpoint might be /admin/uploads
    # Let's try the standard upload flow
    
    # Prepare the upload
    payload = {
        "files": [{
            "name": file_name,
            "type": "text/csv"
        }]
    }
    
    # Note: Medusa v2 upload API might differ. Let's try /admin/uploads
    # Based on logs: POST /admin/uploads/presigned-urls
    # http:    POST /admin/uploads/presigned-urls ← http://localhost:41401/app/products/import (200)
    
    # Actually, let's try to upload directly if possible, or follow the presigned flow.
    # The logs show:
    # POST /admin/uploads/presigned-urls
    # POST /admin/uploads
    # POST /admin/products/imports
    
    # Let's try to use the /admin/uploads endpoint directly with multipart/form-data if it supports it, 
    # but the logs suggest presigned-urls.
    
    # Let's try the presigned url approach first.
    # But wait, if I use the JS SDK it handles this. Here I am using Python.
    
    # Let's try a simpler approach: POST /admin/uploads with the file.
    # Many Medusa versions support this.
    
    with open(file_path, "rb") as f:
        files = {"files": (file_name, f, "text/csv")}
        response = requests.post(f"{BASE_URL}/admin/uploads", headers=HEADERS, files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        # Try the presigned url way if this fails
        return

    data = response.json()
    print(f"Upload Response: {data}")
    print("Upload successful.")
    # The response should contain the file object(s)
    # { "files": [ { "id": "...", "url": "..." } ] }
    
    uploaded_files = data.get("files", [])
    if not uploaded_files:
        print("No files returned.")
        return
        
    file_obj = uploaded_files[0]
    # For local file service, use the ID (filename) as the key, not the full URL.
    file_key = file_obj.get("id")
    
    print(f"Step 2: Triggering import for file key: {file_key}...")
    
    import_payload = {
        "file_key": file_key,
        "originalname": file_name,
        "extension": "csv",
        "size": file_size,
        "mime_type": "text/csv"
    }
    
    response = requests.post(f"{BASE_URL}/admin/products/imports", headers={"Authorization": f"Bearer {ADMIN_TOKEN}", "Content-Type": "application/json"}, json=import_payload)
    
    if response.status_code == 202:
        print("Import started successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"Import failed to start: {response.status_code} - {response.text}")

if __name__ == "__main__":
    import_products("report/product-data/products-medusa-import-final.csv")

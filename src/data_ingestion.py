from azure.storage.blob import BlobServiceClient

def create_blob_client(account_name, account_key):
    return BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )

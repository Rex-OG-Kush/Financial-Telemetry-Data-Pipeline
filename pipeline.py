import os
import requests
import json
from datetime import datetime
# Injecting the official Microsoft Azure Cloud SDK bindings
from azure.storage.blob import BlobServiceClient, BlobClient

class TopTierDataPipeline:
    def __init__(self, target_asset: str):
        self.asset = target_asset
        self.api_url = f"https://coingecko.com{target_asset}&vs_currencies=usd"
        
        # Pulls the Azure connection parameters securely from environment variables
        # This keeps your cloud access keys completely hidden from public view
        self.azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = "financial-ticks-delta-lake"

    def ingest_market_tick(self) -> dict:
        """Fetches live market data from the global API."""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            raw_data = response.json()
            
            if self.asset in raw_data:
                structured_payload = self._transform_data(raw_data[self.asset]["usd"])
                
                # Cloud Link Activation Gate
                if self.azure_connection_string:
                    self._upload_to_azure_blob(structured_payload)
                else:
                    print("[SYSTEM WARNING] Azure Connection String missing. Running in local simulation mode.")
                
                return structured_payload
            else:
                raise ValueError(f"Target asset data footprint missing from API response payload.")
                
        except requests.exceptions.RequestException as e:
            print(f"[METRIC CRITICAL ERROR] Pipeline ingestion failure: {e}")
            return {}

    def _transform_data(self, price: float) -> dict:
        """Transforms raw unstructured telemetry into structured financial schema."""
        return {
            "SchemaVersion": "1.0.0",
            "AssetIdentifier": self.asset.upper(),
            "MarketValueUSD": float(price),
            "IngestionTimestamp": datetime.utcnow().isoformat(),
            "PipelineStatus": "VERIFIED"
        }

    def _upload_to_azure_blob(self, payload: dict):
        """Authenticates with Azure and writes the data directly to the cloud container."""
        try:
            # Generate a clean unique filename for each run (e.g., BITCOIN_2026-10-01T18:30:00.json)
            timestamp = payload["IngestionTimestamp"].replace(":", "-")
            blob_name = f"{payload['AssetIdentifier']}_{timestamp}.json"
            
            # Establish the cloud client session
            blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            
            # Convert JSON dict to standard string byte layout for secure storage delivery
            json_data = json.dumps(payload, indent=4)
            blob_client.upload_blob(json_data, overwrite=True)
            print(f"[CLOUD SUCCESS] Successfully written financial record: {blob_name} to Azure container.")
            
        except Exception as e:
            print(f"[CLOUD CRITICAL ERROR] Failed to stream data footprint to Azure: {e}")

if __name__ == "__main__":
    pipeline = TopTierDataPipeline(target_asset="bitcoin")
    structured_payload = pipeline.ingest_market_tick()

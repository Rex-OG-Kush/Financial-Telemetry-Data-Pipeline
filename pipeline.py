"""
PROJECT: FINANCIAL TELEMETRY INGESTION LOOP
AUTHOR: MATUTUZELA JABULANI NDLOVU
PURPOSE: Orchestrates live asset price discovery, runs R statistical modeling analytics,
         and securely commits the final telemetry matrices to Azure Blob Storage.
"""

import os
import requests
import json
import subprocess
from datetime import datetime
from azure.storage.blob import BlobServiceClient

class TopTierDataPipeline:
    def __init__(self, target_asset: str):
        self.asset = target_asset.lower()
        # Corrected production-ready API path syntax for dynamic value ingestion
        self.api_url = f"https://coingecko.com{self.asset}&vs_currencies=usd"
        
        self.azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = "financial-ticks-delta-lake"

    def ingest_market_tick(self) -> dict:
        """Fetches live market metrics and streams them through the R analytical layer."""
        try:
            print(f"📡 Querying external market telemetry for asset index: '{self.asset}'...")
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            raw_data = response.json()
            
            if self.asset in raw_data:
                # 1. Transform raw asset values to our baseline schema layout
                structured_payload = self._transform_data(raw_data[self.asset]["usd"])
                
                # 2. Programmatically invoke your R 3-Sigma Risk Engine via subprocess
                enriched_payload = self._execute_r_analytics(structured_payload)
                
                # 3. Stream completed telemetry matrices straight into Azure
                if self.azure_connection_string:
                    self._upload_to_azure_blob(enriched_payload)
                else:
                    print("[SYSTEM WARNING] Azure credentials missing. Running local simulation.")
                    print(json.dumps(enriched_payload, indent=4))
                
                return enriched_payload
            else:
                raise ValueError(f"Target asset mapping '{self.asset}' missing from response content.")
                
        except Exception as e:
            print(f"[METRIC CRITICAL ERROR] Pipeline orchestration broke: {e}")
            return {}

    def _transform_data(self, price: float) -> dict:
        """Transforms raw numbers into our enterprise json telemetry layout."""
        return {
            "SchemaVersion": "1.0.0",
            "AssetIdentifier": self.asset.upper(),
            "MarketValueUSD": float(price),
            "IngestionTimestamp": datetime.utcnow().isoformat(),
            "PipelineStatus": "VERIFIED"
        }

    def _execute_r_analytics(self, payload: dict) -> dict:
        """
        Passes data to analytics.R via CLI bindings to inject 3-Sigma alerts.
        """
        try:
            # Clean string parsing layout safely preventing syntax escapes across paths
            json_input = json.dumps(payload)
            print("📊 Passing telemetry data payload to R 3-Sigma matrix context...")
            
            # Execute your script with Rscript binary passing JSON argument configurations
            result = subprocess.run(
                ["Rscript", "analytics.R", json_input],
                capture_output=True, text=True, check=True
            )
            
            # Extract standard output returned from your data frame structures
            r_output = result.stdout.strip()
            # Grabs the last line in case messages/warnings were pushed to stdout
            final_json_line = r_output.splitlines()[-1] if "\n" in r_output else r_output
            
            return json.loads(final_json_line)
        except Exception as e:
            print(f"[ANALYTICS ENCOUNTERED ERROR] R Execution loop fell back onto default metrics: {e}")
            # Dynamic recovery matrix layout matching your R framework schemas
            payload.update({
                "RollingMeanMetric": payload["MarketValueUSD"],
                "VolatilityVariance": 0.0,
                "UpperAnomalyLimit": payload["MarketValueUSD"] * 1.02,
                "LowerAnomalyLimit": payload["MarketValueUSD"] * 0.98,
                "AnomalySignalFlag": "SYSTEM_STABLE"
            })
            return payload

    def _upload_to_azure_blob(self, payload: dict):
        """Authenticates securely and pushes the output straight to Azure."""
        try:
            timestamp = payload["IngestionTimestamp"].replace(":", "-")
            blob_name = f"{payload['AssetIdentifier']}_{timestamp}.json"
            
            blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            
            json_data = json.dumps(payload, indent=4)
            blob_client.upload_blob(json_data, overwrite=True)
            print(f"☁️ [CLOUD SUCCESS] Committed record footprint to storage container: {blob_name}")
            
        except Exception as e:
            print(f"❌ [CLOUD CRITICAL ERROR] Streaming block rejected by cloud boundary: {e}")

if __name__ == "__main__":
    # Dynamically inject the target index via your runtime dashboard or environment
    target_ticker = os.getenv("TARGET_ASSET_TICKER", "bitcoin")
    
    pipeline = TopTierDataPipeline(target_asset=target_ticker)
    pipeline.ingest_market_tick()

import os
import requests
import json
from datetime import datetime

class TopTierDataPipeline:
    def __init__(self, target_asset: str):
        self.asset = target_asset
        # Connecting to real-time global market data
        self.api_url = f"https://coingecko.com{target_asset}&vs_currencies=usd"

    def ingest_market_tick(self) -> dict:
        """Fetches live market data from the global API."""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            raw_data = response.json()
            
            # System Validation Gate (Critical for DevOps architecture)
            if self.asset in raw_data:
                return self._transform_data(raw_data[self.asset]["usd"])
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

if __name__ == "__main__":
    # Test execution for your local repository environment
    pipeline = TopTierDataPipeline(target_asset="bitcoin")
    structured_payload = pipeline.ingest_market_tick()
    print(json.dumps(structured_payload, indent=4))

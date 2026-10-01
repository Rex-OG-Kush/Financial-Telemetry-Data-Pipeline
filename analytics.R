# ==============================================================================
# FINANCIAL TELEMETRY RISK ENGINE - DATA SCIENCE METRIC PIPELINE
# Framework: HarvardX Advanced Data Modeling & Anomaly Mapping Validation
# ==============================================================================

library(dplyr)
library(jsonlite)

compute_asset_volatility_from_cli <- function() {
  # Collect systemic parameters passed down via command execution paths
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) == 0) {
    # Default fallback string keeping your simulation workspace working cleanly
    raw_json_payload <- '{"SchemaVersion":"1.0.0","AssetIdentifier":"BITCOIN","MarketValueUSD":63450.00,"IngestionTimestamp":"2026-10-01T17:16:45","PipelineStatus":"VERIFIED"}'
  } else {
    raw_json_payload <- args[1]
  }
  
  tryCatch({
    data_frame <- fromJSON(raw_json_payload) %>% as.data.frame()
    
    required_fields <- c("AssetIdentifier", "MarketValueUSD", "IngestionTimestamp")
    if (!all(required_fields %in% colnames(data_frame))) {
      stop("Incoming telemetry payload violates schema standard parameters.")
    }
    
    market_price <- as.numeric(data_frame$MarketValueUSD)
    rolling_mean  <- mean(market_price)
    std_deviation <- sd(market_price)
    
    if (is.na(std_deviation) || std_deviation == 0) {
      std_deviation <- rolling_mean * 0.02 
    }
    
    upper_deviation_gate <- rolling_mean + (3 * std_deviation)
    lower_deviation_gate <- rolling_mean - (3 * std_deviation)
    
    processed_insights <- data_frame %>%
      mutate(
        RollingMeanMetric   = rolling_mean,
        VolatilityVariance  = std_deviation,
        UpperAnomalyLimit   = upper_deviation_gate,
        LowerAnomalyLimit   = lower_deviation_gate,
        AnomalySignalFlag   = ifelse(MarketValueUSD >= upper_deviation_gate | MarketValueUSD <= lower_deviation_gate, "ANOMALY_DETECTED", "SYSTEM_STABLE")
      )
    
    # Converts data arrays directly back into compact un-escaped JSON outputs
    cat(toJSON(as.list(processed_insights), auto_unbox = TRUE))
    
  }, error = function(err) {
    # Fail-safe print formatting matching pipeline string capture paradigms
    fallback_payload <- paste0('{"PipelineStatus":"FAILED","ErrorMessage":"', err$message, '"}')
    cat(fallback_payload)
  })
}

# Fire execution context instantly when called by orchestration routines
compute_asset_volatility_from_cli()

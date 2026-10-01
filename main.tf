# 1. Establish the cloud platform governance bindings
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# 2. Form a secure resource isolation perimeter (Resource Group)
resource "azurerm_resource_group" "rg" {
  name     = "rg-financial-telemetry-prod"
  location = "southafricanorth" # Deploys directly to the Johannesburg region to guarantee minimal latency loops
}

# 3. Provision a secure storage firewall cluster
resource "azurerm_storage_account" "storage" {
  name                     = "stquanttelemetryprod001" # Must be globally unique across Azure
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # Locally Redundant Storage for cost optimization
}

# 4. Form the data repository boundary for the JSON payloads
resource "azurerm_storage_container" "container" {
  name                  = "financial-ticks-delta-lake"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private" # Restricts all external public read paths to ensure absolute data defense
}

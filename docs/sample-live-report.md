# Sample Live Governance Report

_Generated against a real Azure subscription via the Azure SDK. Resource group/IP names generalized for the public repo._

## Summary

- Total Resource Groups: 5
- Resource Groups Without Lock: 4
- Unattached Disks: 0
- Unassociated Public IPs: 1
- Total Findings: 5

## Findings

- **Medium** – rg-lab-01: Resource group has no delete lock — at risk of accidental deletion
- **Medium** – NetworkWatcherRG: Resource group has no delete lock — at risk of accidental deletion
- **Medium** – rg-final-project: Resource group has no delete lock — at risk of accidental deletion
- **Medium** – rg-sc200-lab01: Resource group has no delete lock — at risk of accidental deletion
- **Low** – sample-vnet-ip: Unassociated public IP — incurring cost with no active use

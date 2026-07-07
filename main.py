import csv
import json
import os

from azure_client import fetch_live_governance_data

DATA_FILE = "data/sample_governance.json"
REPORT_FILE = "governance_report.csv"
REPORT_MD_FILE = "governance_report.md"


def load_governance_data():
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")

    if subscription_id:
        try:
            print(f"\nFetching live governance data from Azure subscription {subscription_id}...")
            return fetch_live_governance_data(subscription_id)
        except Exception as error:
            print(f"\nCould not fetch live governance data: {error}")
            print("Falling back to local sample data.")

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"\nData file not found: {DATA_FILE}")
        return {"resource_groups": [], "unattached_disks": [], "unassociated_public_ips": []}


def show_resource_groups(data):
    print("\n=== Resource Groups ===")

    resource_groups = data["resource_groups"]

    if not resource_groups:
        print("No resource groups found.")
        return

    for rg in resource_groups:
        lock_status = "Locked" if rg["has_lock"] else "No Lock"
        print(f"- {rg['name']} ({rg['location']}) — {lock_status}")


def show_unattached_disks(data):
    print("\n=== Unattached Managed Disks ===")

    disks = data["unattached_disks"]

    if not disks:
        print("No unattached disks found.")
        return

    for disk in disks:
        print(f"- {disk['name']} in {disk['resource_group']} ({disk['size_gb']} GB)")


def show_unassociated_public_ips(data):
    print("\n=== Unassociated Public IPs ===")

    public_ips = data["unassociated_public_ips"]

    if not public_ips:
        print("No unassociated public IPs found.")
        return

    for public_ip in public_ips:
        print(f"- {public_ip['name']} in {public_ip['resource_group']}")


def show_summary(data):
    print("\n=== Governance Summary ===")

    resource_groups = data["resource_groups"]
    unlocked_groups = [rg for rg in resource_groups if not rg["has_lock"]]

    print(f"Total Resource Groups: {len(resource_groups)}")
    print(f"Resource Groups Without Lock: {len(unlocked_groups)}")
    print(f"Unattached Disks: {len(data['unattached_disks'])}")
    print(f"Unassociated Public IPs: {len(data['unassociated_public_ips'])}")


def build_governance_findings(data):
    findings = []

    for rg in data["resource_groups"]:
        if not rg["has_lock"]:
            findings.append({
                "resource": rg["name"],
                "severity": "Medium",
                "finding": "Resource group has no delete lock — at risk of accidental deletion",
            })

    for disk in data["unattached_disks"]:
        findings.append({
            "resource": disk["name"],
            "severity": "Low",
            "finding": f"Unattached managed disk ({disk['size_gb']} GB) — incurring cost with no active use",
        })

    for public_ip in data["unassociated_public_ips"]:
        findings.append({
            "resource": public_ip["name"],
            "severity": "Low",
            "finding": "Unassociated public IP — incurring cost with no active use",
        })

    return findings


def count_findings_by_severity(findings, severity):
    count = 0

    for finding in findings:
        if finding["severity"] == severity:
            count += 1

    return count


def show_governance_findings(data):
    print("\n=== Governance Findings ===")

    findings = build_governance_findings(data)

    if not findings:
        print("No governance findings found.")
        return

    for index, finding in enumerate(findings, start=1):
        print(f"\nFinding #{index}")
        print("----------------------------------------")
        print(f"Resource: {finding['resource']}")
        print(f"Severity: {finding['severity']}")
        print(f"Finding: {finding['finding']}")

    print("\nFindings Summary")
    print(f"Total Findings: {len(findings)}")
    print(f"High: {count_findings_by_severity(findings, 'High')}")
    print(f"Medium: {count_findings_by_severity(findings, 'Medium')}")
    print(f"Low: {count_findings_by_severity(findings, 'Low')}")


def export_to_csv(data):
    print("\n=== Export Governance Findings ===")

    findings = build_governance_findings(data)

    if not findings:
        print("No findings to export.")
        return

    with open(REPORT_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["resource", "severity", "finding"])
        writer.writeheader()
        writer.writerows(findings)

    print(f"\nGovernance report exported successfully to {REPORT_FILE}")


def build_markdown_report(data):
    lines = ["# Azure Governance Analyzer Report", ""]

    findings = build_governance_findings(data)
    unlocked_groups = [rg for rg in data["resource_groups"] if not rg["has_lock"]]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total Resource Groups: {len(data['resource_groups'])}")
    lines.append(f"- Resource Groups Without Lock: {len(unlocked_groups)}")
    lines.append(f"- Unattached Disks: {len(data['unattached_disks'])}")
    lines.append(f"- Unassociated Public IPs: {len(data['unassociated_public_ips'])}")
    lines.append(f"- Total Findings: {len(findings)}")
    lines.append("")

    lines.append("## Findings")
    lines.append("")

    if not findings:
        lines.append("No governance findings.")
    else:
        for finding in findings:
            lines.append(f"- **{finding['severity']}** – {finding['resource']}: {finding['finding']}")

    lines.append("")

    return "\n".join(lines)


def export_to_markdown(data):
    print("\n=== Export Governance Report (Markdown) ===")

    report = build_markdown_report(data)

    with open(REPORT_MD_FILE, "w") as file:
        file.write(report)

    print(f"\nGovernance report exported successfully to {REPORT_MD_FILE}")


def main():
    data = load_governance_data()

    print("=" * 40)
    print("Azure Governance Analyzer")
    print("=" * 40)

    while True:
        print("\n1. Show Resource Groups")
        print("2. Show Unattached Disks")
        print("3. Show Unassociated Public IPs")
        print("4. Show Summary")
        print("5. Show Governance Findings")
        print("6. Export to CSV")
        print("7. Export to Markdown")
        print("8. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            show_resource_groups(data)

        elif choice == "2":
            show_unattached_disks(data)

        elif choice == "3":
            show_unassociated_public_ips(data)

        elif choice == "4":
            show_summary(data)

        elif choice == "5":
            show_governance_findings(data)

        elif choice == "6":
            export_to_csv(data)

        elif choice == "7":
            export_to_markdown(data)

        elif choice == "8":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()

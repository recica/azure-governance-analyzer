from azure.identity import DefaultAzureCredential
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.locks import ManagementLockClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient


def fetch_resource_groups(resource_client, lock_client):
    resource_groups = []

    for rg in resource_client.resource_groups.list():
        locks = list(lock_client.management_locks.list_at_resource_group_level(rg.name))

        resource_groups.append({
            "name": rg.name,
            "location": rg.location,
            "has_lock": len(locks) > 0,
        })

    return resource_groups


def fetch_unattached_disks(compute_client):
    unattached_disks = []

    for disk in compute_client.disks.list():
        if disk.managed_by:
            continue

        resource_group = disk.id.split("/")[4]

        unattached_disks.append({
            "name": disk.name,
            "resource_group": resource_group,
            "location": disk.location,
            "size_gb": disk.disk_size_gb,
        })

    return unattached_disks


def fetch_unassociated_public_ips(network_client):
    unassociated_public_ips = []

    for public_ip in network_client.public_ip_addresses.list_all():
        if public_ip.ip_configuration:
            continue

        resource_group = public_ip.id.split("/")[4]

        unassociated_public_ips.append({
            "name": public_ip.name,
            "resource_group": resource_group,
            "location": public_ip.location,
        })

    return unassociated_public_ips


def fetch_live_governance_data(subscription_id):
    credential = DefaultAzureCredential()
    resource_client = ResourceManagementClient(credential, subscription_id)
    lock_client = ManagementLockClient(credential, subscription_id)
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    return {
        "resource_groups": fetch_resource_groups(resource_client, lock_client),
        "unattached_disks": fetch_unattached_disks(compute_client),
        "unassociated_public_ips": fetch_unassociated_public_ips(network_client),
    }

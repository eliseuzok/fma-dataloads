"""
Functions for querying the Gateway MongoDB database.
"""

import pymongo
import numpy as np

from .exceptions import CriticalError


def get_gateway_datasets(
    db: pymongo.database.Database = None, publisher: dict = None
) -> list:
    """
    Get a list of datasets from the Gateway relevant to a given custodian (i.e., publisher).
    """
    try:
        datasets = db.sync.find(
            {"publisherName": publisher},
        )

        return datasets
    except Exception as error:
        raise CriticalError(
            f"Error retrieving gateway datasets for publisher {publisher}: {error}"
        ) from error


def get_latest_gateway_dataset(
    db: pymongo.database.Database = None, pid: str = ""
) -> dict:
    """
    Get the latest version of a given dataset from the tools collection in the Gateway
    """
    try:
        datasets = db.tools.find({"type": "dataset", "pid": pid}).sort("createdAt", -1)

        return datasets[0]
    except IndexError:
        return None
    except Exception as error:
        raise CriticalError(
            f"Error retrieving latest version of dataset {pid} from the Gateway: {error}"
        ) from error


def archive_gateway_datasets(
    db: pymongo.database.Database = None, archived_datasets: np.array = None
) -> None:
    """
    Archive datasets on the Gateway given a list of datasets (which are then mapped to IDs).
    """
    try:
        db.tools.update_many(
            {"pid": {"$in": list(map(lambda x: x["pid"], archived_datasets))}},
            {"$set": {"activeflag": "archive"}},
        )
    except Exception as error:
        raise CriticalError(
            f"Error archiving datasets on the Gateway: {error}"
        ) from error


def add_new_datasets(db: pymongo.database.Database = None, new_datasets=None) -> None:
    """
    Add new datasets to the Gateway given a list of datasets.
    """
    try:
        db.tools.insert_many(new_datasets)
    except Exception as error:
        raise CriticalError(
            f"Error inserting list of new datasets into the Gateway: {error}"
        ) from error


def get_publisher(
    db: pymongo.database.Database = None, publisher_name: str = ""
) -> dict:
    """
    Get the relevant publisher documentation given a publisher name.
    """
    try:
        return db.publishers.find_one({"publisherDetails.name": publisher_name})
    except Exception as error:
        raise CriticalError(
            f"Error retrieving the publisher details from the publisher collection for publisher name {publisher_name}: {error}"
        ) from error


def update_publisher(
    db: pymongo.database.Database = None, status: str = "", publisher_name: str = ""
) -> None:
    """
    Update the federation status of a publisher, e.g., True/False.
    """
    try:
        db.publishers.update_one(
            {"publisherDetails.name": publisher_name},
            {"$set": {"federation.active": status}},
        )
    except Exception as error:
        raise CriticalError(
            f"Error setting the federation.status of publisher {publisher_name}: {error}"
        ) from error


def sync_datasets(db: pymongo.database.Database = None, sync_list: list = None) -> None:
    """
    Remove any existing sync status for a given PID and add new sync entry.
    """
    try:
        db.sync.delete_many({"pid": {"$in": list(map(lambda x: x["pid"], sync_list))}})
        db.sync.insert_many(sync_list)
    except Exception as error:
        raise CriticalError(
            f"Error updating the sync collection on the Gateway: {error}"
        ) from error

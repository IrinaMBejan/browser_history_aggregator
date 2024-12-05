import os
import sqlite3
import platform
from datetime import datetime, timedelta
from syftbox.lib import Client
from typing import List, Dict, Tuple
import shutil
from pathlib import Path
import json


API_NAME = "browser_history"


def hamming_distance_between_hashes(user_hashes:Dict[str,List[str]]) -> Dict[Tuple[str,str],float]:
    """
    Calculate the Hamming distance between each pair of values (lists of strings) in a dictionary.
    
    Parameters:
        user_hashes (dict): A dictionary where keys are IDs and values are lists of strings.
    
    Returns:
        dict: A dictionary where keys are tuple pairs of IDs and values are their Hamming distances.
    """
    def calculate_hamming(str1, str2):
        """Calculate Hamming distance between two strings of equal length."""
        if len(str1) != len(str2):
            raise ValueError("Strings must be of equal length for Hamming distance.")
        return sum(ch1 != ch2 for ch1, ch2 in zip(str1, str2))

    keys = list(user_hashes.keys())
    n = len(keys)

    if n < 2:
        raise ValueError("There must be at least two entries to compare.")

    # Ensure all lists in the dictionary have the same length
    first_length = len(user_hashes[keys[0]])
    for key, lst in user_hashes.items():
        if len(lst) != first_length:
            raise ValueError("All lists in the dictionary must have the same number of strings.")

    # Calculate Hamming distance for each pair of IDs
    result = {}
    for i in range(n):
        for j in range(i + 1, n):
            id1, id2 = keys[i], keys[j]
            hamming_distance = 0
            for str1, str2 in zip(user_hashes[id1], user_hashes[id2]):
                hamming_distance += calculate_hamming(str1, str2)
            result[(id1, id2)] = hamming_distance

    return result


def network_participants(datasite_path: Path):
    """
    Retrieves a list of user directories (participants) in a given datasite path.

    Args:
        datasite_path (Path): The path to the datasite directory containing user subdirectories.

    Returns:
        list: A list of strings representing the names of the user directories present in the datasite path.

    Example:
        If the datasite_path contains the following directories:
        - datasite/user1/
        - datasite/user2/
        Then the function will return:
        ['user1', 'user2']
    """
    # Get all entries in the specified datasite path
    entries = os.listdir(datasite_path)

    # Initialize an empty list to store user directory names
    users = []

    # Iterate through each entry and add to users list if it's a directory
    for entry in entries:
        if Path(datasite_path / entry).is_dir():
            users.append(entry)

    # Return the list of user directories
    return users

def is_updated(timestamp: str) -> bool:
    """
    Checks if a given timestamp is within the last 10 seconds of the current time.

    Args:
        timestamp (str): The timestamp string in the format "%Y-%m-%d %H:%M:%S".

    Returns:
        bool: True if the timestamp is within the last 10 seconds from now, False otherwise.

    Example:
        If the current time is "2024-10-05 14:00:30" and the given timestamp is
        "2024-10-05 14:00:25", the function will return True.
    """
    # Parse the provided timestamp string into a datetime object
    data_timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    # Get the current time as a datetime object
    current_time = datetime.now()

    # Calculate the time difference between now and the provided timestamp
    time_diff = current_time - data_timestamp

    # Return True if the timestamp is within the last 10 seconds
    return time_diff < timedelta(minutes=1)

def get_score_from_browser_history_hashes(
    datasites_path: Path, peers: list[str]
) -> Tuple[List[str], List[List[str]]]:
    """
    Calculates the similarity across a network of peers.

    Args:
        datasites_path (Path): The path to the directory containing data for all peers.
        peers (list[str]): A list of peer directory names.

    Returns:
        float: The mean CPU usage of the peers whose data is available and updated.
               Returns -1 if no data is available or no peers have been updated recently.

    Example:
        If `datasites_path` is "/datasites" and the list of peers is ["peer1", "peer2"],
        this function will attempt to read CPU usage data from files located at:
        - "/datasites/peer1/api_data/browser_history/browser_history.json"
        - "/datasites/peer2/api_data/browser_history/browser_history.json"
        It then computes the average CPU usage for peers with valid and updated data.
    """
    # Initialize variables for aggregated similarity and peer count
    user_hashes = {}
    active_peers = []
    # Iterate over each peer to gather CPU usage data
    for peer in peers:
        # Construct the path to the CPU tracker JSON file for the peer
        tracker_file: Path = (
            datasites_path / peer / "api_data" / "browser_history" / "browser_history_public.json"
        )
        # Skip if the tracker file does not exist
        if not tracker_file.exists():
            continue

        # Open and read the JSON file for the peer
        with open(str(tracker_file), "r") as json_file:
            try:
                peer_data = json.load(json_file)
            except json.JSONDecodeError:
                # Skip if the JSON file cannot be decoded properly
                continue

        # Check if the data is updated and add to aggregation if valid
        if "timestamp" in peer_data and is_updated(peer_data["timestamp"]):
            user_hashes[peer] = peer_data["browser_history"]
            active_peers.append(peer)

    # Calculate the mean CPU usage if there are valid peers with updated data
    if len(active_peers) >= 2:
        hamming_distance = hamming_distance_between_hashes(user_hashes=user_hashes)
    else:
        hamming_distance = {}

    # Return the calculated mean CPU usage or -1 if no data is available
    return hamming_distance, active_peers

def copy_html_files(source: Path, destination: Path):
    """
    Moves all files from the source directory to the destination directory.

    Args:
        source (Path): The source directory.
        destination (Path): The destination directory.

    Raises:
        ValueError: If source or destination is not a directory.
    """
    if not source.is_dir():
        raise ValueError(f"Source {source} is not a directory.")
    if not destination.exists():
        destination.mkdir(parents=True)
    elif not destination.is_dir():
        raise ValueError(f"Destination {destination} is not a directory.")

    for item in source.iterdir():
        if item.is_file():
            target = destination / item.name
            try:
                os.rename(item, target)
            except Exception as e:
                print(f"Error moving file {item} to {target}: {e}")

def should_run() -> bool:
    INTERVAL = 20  # 20 seconds
    timestamp_file = f"./script_timestamps/{API_NAME}_last_run"
    os.makedirs(os.path.dirname(timestamp_file), exist_ok=True)
    now = datetime.now().timestamp()
    time_diff = INTERVAL  # default to running if no file exists
    if os.path.exists(timestamp_file):
        try:
            with open(timestamp_file, "r") as f:
                last_run = int(f.read().strip())
                time_diff = now - last_run
        except (FileNotFoundError, ValueError):
            print(f"Unable to read timestamp file: {timestamp_file}")
    if time_diff >= INTERVAL:
        with open(timestamp_file, "w") as f:
            f.write(f"{int(now)}")
        return True
    return False


if __name__ == "__main__":
    if not should_run():
        print(f"Skipping {API_NAME}, not enough time has passed.")
        exit(0)
        
    client = Client.load()
    # For adding UI files
    copy_html_files(
        source=Path("./assets"), destination=client.datasite_path / "public"
    )

    peers = network_participants(client.datasite_path.parent)

    hamming_distance, active_peers = get_score_from_browser_history_hashes(client.datasite_path.parent, peers)

    output_public_file = client.datasite_path / "public" / "browser_history.json"

    # If there's at least one active_peer
    # if len(active_peers):
    #     truncate_file(
    #         file_path=output_public_file,
    #         max_items=360,
    #         new_sample=cpu_mean,
    #         peers=active_peers,
    #     )
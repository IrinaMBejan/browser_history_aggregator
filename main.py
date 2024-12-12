import os
from datetime import datetime, timedelta
from syftbox.lib import Client
from typing import Counter, List, Dict, Tuple, DefaultDict
import shutil
from pathlib import Path
import json

from typing import Dict, List, Set, Tuple
# from collections import Counter

API_NAME = "browser_history"

OUT_NAME = "browser_history_agg"


def compare_users_exact_match(
    users_domains: Dict[str, List[str]],
) -> List[Tuple[str, str, float, Set[str]]]:
    """
    Compare users based on exact domain matches.

    Args:
        users_domains: Dictionary mapping user IDs to their domain lists

    Returns:
        List of tuples (user1, user2, similarity_score, common_domains)
        where similarity_score is percentage of shared domains
    """
    matches = DefaultDict(list)
    users = list(users_domains.keys())

    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            user1, user2 = users[i], users[j]

            domains1 = set(users_domains[user1])
            domains2 = set(users_domains[user2])

            common_domains = domains1 & domains2

            # Calculate similarity as percentage of shared domains
            total_unique_domains = len(domains1 | domains2)
            if total_unique_domains > 0:
                similarity = len(common_domains) / total_unique_domains
                if similarity > 0:
                    matches[user1].append((user2, similarity))
                    matches[user2].append((user1, similarity))

    for user, _ in matches.items():
        matches[user].sort(key=lambda x: x[1], reverse=True)

    return matches


# def hamming_distance_between_hashes(user_hashes:Dict[str,List[str]]) -> Dict[Tuple[str,str],float]:
#     """
#     Calculate the Hamming distance between each pair of values in a dictionary and return JSON-compatible output.

#     Parameters:
#         user_hashes (dict): A dictionary where keys are IDs and values are lists of strings.

#     Returns:
#         dict: A dictionary where each key is an ID, and the value is a list of Hamming distances
#               to other IDs in the same order as the keys.
#     """
#     def calculate_hamming(str1, str2):
#         """Calculate Hamming distance between two strings of equal length."""
#         if len(str1) != len(str2):
#             raise ValueError("Strings must be of equal length for Hamming distance.")
#         return sum(ch1 != ch2 for ch1, ch2 in zip(str1, str2))

#     ids = list(user_hashes.keys())
#     n = len(ids)

#     if n < 2:
#         raise ValueError("There must be at least two entries to compare.")

#     # Ensure all lists in the dictionary have the same length
#     first_length = len(user_hashes[ids[0]])
#     for key, lst in user_hashes.items():
#         if len(lst) != first_length:
#             raise ValueError("All lists in the dictionary must have the same number of strings.")

#     # Initialize result dictionary
#     result = {id_: [] for id_ in ids}

#     # Calculate Hamming distances
#     for i in range(n):
#         id1 = ids[i]
#         for j in range(n):
#             id2 = ids[j]
#             if i == j:
#                 # Distance to itself is 0
#                 result[id1].append(0)
#             else:
#                 hamming_distance = 0
#                 for str1, str2 in zip(user_hashes[id1], user_hashes[id2]):
#                     hamming_distance += calculate_hamming(str1, str2)
#                 result[id1].append(hamming_distance)

#     return result


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


def get_score_from_browser_history_hashes(
    datasites_path: Path, peers: list[str]
) -> Tuple[Dict[str, List[str]], List[List[str]]]:
    """
    Calculates the similarity across a network of peers.

    Args:
        datasites_path (Path): The path to the directory containing data for all peers.
        peers (list[str]): A list of peer directory names.

    Returns:
        similarity: Similarity between peers
    """
    user_hashes = {}
    active_peers = []

    for peer in peers:
        tracker_file: Path = (
            datasites_path
            / peer
            / "api_data"
            / API_NAME
            / "browser_history_enc.json"
        )
        if not tracker_file.exists():
            continue

        with open(str(tracker_file), "r") as json_file:
            try:
                peer_data = json.load(json_file)
            except json.JSONDecodeError:
                continue

        user_hashes[peer] = peer_data["browser_history"]
        active_peers.append(peer)

    if len(active_peers) >= 2:
        similarity_matrix = compare_users_exact_match(users_domains=user_hashes)
    else:
        similarity_matrix = {}

    return similarity_matrix, active_peers


def get_top_domains(
    datasites_path: Path, peers: list[str], count: int
) -> Tuple[Dict[str, int], List[List[str]]]:

    """
    Calculates the most viewed domains

    Args:
        datasites_path (Path): The path to the directory containing data for all peers.
        peers (list[str]): A list of peer directory names.
        count: (int): The number of top domains to return.

    Returns:
        domains: list of domains
    """
    active_peers = []
    all_domains = []

    for peer in peers:
        tracker_file: Path = (
            datasites_path / peer / "api_data" / API_NAME / "browser_history_clear.json"
        )
        if not tracker_file.exists():
            continue

        with open(str(tracker_file), "r") as json_file:
            try:
                peer_data = json.load(json_file)
            except json.JSONDecodeError:
                continue

        all_domains.extend(peer_data["browser_history"])
        active_peers.append(peer)

    domain_counts = Counter(all_domains)
    return domain_counts.most_common(count), active_peers


def get_top_papers(
    datasites_path: Path, peers: list[str], count: int
) -> Tuple[Dict[str, int], List[List[str]]]:
    """
    Calculates the top 10 most papers read.

    Args:
        datasites_path (Path): The path to the directory containing data for all peers.
        peers (list[str]): A list of peer directory names.
        count: (int): The number of top domains to return.

    Returns:
        domains: list of domains
    """
    active_peers = []
    all_domains = []

    for peer in peers:
        tracker_file: Path = (
            datasites_path
            / peer
            / "api_data"
            / "browser_history"
            / "browser_history_enc.json"
        )
        if not tracker_file.exists():
            continue

        with open(str(tracker_file), "r") as json_file:
            try:
                peer_data = json.load(json_file)
            except json.JSONDecodeError:
                continue

    for peer in peers:
        tracker_file: Path = (
            datasites_path / peer / "api_data" / API_NAME / "paper_stats.json"
        )
        if not tracker_file.exists():
            continue

        with open(str(tracker_file), "r") as json_file:
            try:
                peer_data = json.load(json_file)
            except json.JSONDecodeError:
                continue

        all_domains.extend(peer_data["papers"])
        active_peers.append(peer)

    domain_counts = Counter(all_domains)
    return domain_counts.most_common(count), active_peers


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
        source=Path("./assets"), destination=client.datasite_path / "public" / OUT_NAME
    )

    peers = network_participants(client.datasite_path.parent)

    similarity, active_peers = get_score_from_browser_history_hashes(
        client.datasite_path.parent, peers
    )
    top_domains, active_peers = get_top_domains(
        client.datasite_path.parent, peers, count=5
    )
    top_papers, active_peers = get_top_papers(
        client.datasite_path.parent, peers, count=10
    )

    output_similarity = (
        client.datasite_path
        / "public"
        / OUT_NAME
        / "outputs"
        / "output_similarity.json"
    )
    with open(output_similarity, "w") as f:
        json.dump(similarity, f)

    output_most_domains = (
        client.datasite_path
        / "public"
        / OUT_NAME
        / "outputs"
        / "output_most_viewed_domains.json"
    )
    with open(output_most_domains, "w") as f:
        json.dump(top_domains, f)

    output_peers = (
        client.datasite_path / "public" / OUT_NAME / "outputs" / "output_peers.json"
    )
    with open(output_peers, "w") as f:
        json.dump(active_peers, f)

    output_top_papers = (
        client.datasite_path
        / "public"
        / OUT_NAME
        / "outputs"
        / "output_top_papers.json"
    )
    with open(output_top_papers, "w") as f:
        json.dump(top_papers, f)

import json
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

def process_lines_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    begin_line_index = next(i for i, line in enumerate(lines) if "Begin synthetic workload!" in line)
    
    # Process lines after the synthetic workload begins, ignoring all duplicate lines containing "[virt:", and memory failures
    data = []
    for line in lines[begin_line_index + 1:]:
        if "[virt:" in line or "malloc failed: AllocFailed" in line or "Untyped Retype: Insufficient memory" in line:
            continue
        if "Done :)" in line:
            break  # Stop processing after this line
        try:
            json_str = line[line.index('{'):line.rindex('}')+1]
            json_str_corrected = json_str.replace("'", '"')  # Correcting for single-quote JSON-like format
            json_data = json.loads(json_str_corrected)

            if all(key in json_data for key in ["bytes requested", "bytes in-use", "lhs fragmentation", "in-between fragmentation"]):
                data.append({
                    "bytes_requested": json_data["bytes requested"],
                    "bytes_in_use": json_data["bytes in-use"],
                    "lhs_fragmentation": json_data["lhs fragmentation"],
                    "in_between_fragmentation": json_data["in-between fragmentation"],
                })
        except Exception as e:
            continue  # Skip lines that do not contain valid JSON data or have other issues

    return data

def plot_metrics(data, args: argparse.Namespace):
    # Extracting data for plotting
    bytes_requested = [entry["bytes_requested"] for entry in data]
    bytes_in_use = [entry["bytes_in_use"] for entry in data]
    lhs_fragmentation = [entry["lhs_fragmentation"] for entry in data]
    in_between_fragmentation = [entry["in_between_fragmentation"] for entry in data]

    # Creating separate plots for each metric
    fig, axs = plt.subplots(3, 1, figsize=(14, 21))

    # Plot for Bytes in Use
    axs[0].plot(bytes_requested, bytes_in_use, label="Bytes in Use", marker='o', color='blue')
    axs[0].set_xlabel('Bytes Requested')
    axs[0].set_ylabel('Bytes in Use')
    axs[0].set_title('Bytes in Use vs. Bytes Requested')
    axs[0].grid(True)
    axs[0].legend()

    # Plot for LHS Fragmentation
    axs[1].plot(bytes_requested, lhs_fragmentation, label="LHS Fragmentation", marker='x', color='red')
    axs[1].set_xlabel('Bytes Requested')
    axs[1].set_ylabel('LHS Fragmentation')
    axs[1].set_title('LHS Fragmentation vs. Bytes Requested')
    axs[1].grid(True)
    axs[1].legend()

    # Plot for In-Between Fragmentation
    axs[2].plot(bytes_requested, in_between_fragmentation, label="In-Between Fragmentation", marker='^', color='green')
    axs[2].set_xlabel('Bytes Requested')
    axs[2].set_ylabel('In-Between Fragmentation')
    axs[2].set_title('In-Between Fragmentation vs. Bytes Requested')
    axs[2].grid(True)
    axs[2].legend()

    plt.tight_layout()
    plt.savefig(f"{Path(args.run_log_file).name.split('.')[-2]}.png")
    plt.show()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
            description="Process results from a single performance eval run. Plot the results"
            )

    parser.add_argument(
            "--run_log_file",
            type=str,
            required=True,
            help="Path to the log file produced by the robot script, running the workload on CantripOS.",
            )

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    file_path = args.run_log_file

    data = process_lines_from_file(file_path)
    print("plotting..")
    plot_metrics(data, args)


import json
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from os import makedirs

def process_lines_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # TODO: this is dirty, print statements at the start of a run need to be unified!
    try:
        begin_line_index = next(i for i, line in enumerate(lines) if "Begin synthetic workload!" in line)
    except StopIteration:
        try:
            print("Not a synthetic workload, checking if a standalone application workload")
            begin_line_index = next(i for i, line in enumerate(lines) if "replay_app" in line)
        except StopIteration:
            print("Not a standalone application workload, chekcing if sequential application workload")
            begin_line_index = next(i for i, line in enumerate(lines) if "replay_seq_app" in line)
    
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

def plot_metrics(best_data, next_data, args: argparse.Namespace):
    # Extracting data for plotting
    best_bytes_requested = [entry["bytes_requested"] for entry in best_data]
    best_bytes_in_use = [entry["bytes_in_use"] for entry in best_data]
    best_lhs_fragmentation = [entry["lhs_fragmentation"] for entry in best_data]
    best_in_between_fragmentation = [entry["in_between_fragmentation"] for entry in best_data]

    next_bytes_requested = [entry["bytes_requested"] for entry in next_data]
    next_bytes_in_use = [entry["bytes_in_use"] for entry in next_data]
    next_lhs_fragmentation = [entry["lhs_fragmentation"] for entry in next_data]
    next_in_between_fragmentation = [entry["in_between_fragmentation"] for entry in next_data]

    # Creating separate plots for each metric
    fig, axs = plt.subplots(3, 1, figsize=(14, 21))

    # Plot for Bytes in Use
    axs[0].plot(best_bytes_requested, best_bytes_in_use, label="Best Fit - Bytes in Use", marker=',', color='blue')
    if args.separate_axis:
        ax2 = axs[0].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - Bytes in Use')
        ax2.plot(next_bytes_requested, next_bytes_in_use, label="Next Fit - Bytes in Use", marker=',', color='blue', linestyle="dotted")
        axs[0].set_ylabel('Best Fit - Bytes in Use')
    else:
        axs[0].plot(next_bytes_requested, next_bytes_in_use, label="Next Fit - Bytes in Use", marker=',', color='blue', linestyle="dotted")
        axs[0].set_ylabel('Bytes in Use')
    axs[0].set_xlabel('Bytes Requested')
    axs[0].set_title('Bytes in Use vs. Bytes Requested')
    axs[0].grid(True)
    axs[0].legend()

    # Plot for LHS Fragmentation
    axs[1].plot(best_bytes_requested, best_lhs_fragmentation, label="Best Fit - LHS Fragmentation", marker=',', color='red')
    if args.separate_axis:
        ax2 = axs[1].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - LHS Fragmentation')
        ax2.plot(next_bytes_requested, next_lhs_fragmentation, label="Next Fit - LHS Fragmentation", marker=',', color='red', linestyle="dotted")
        axs[1].set_ylabel('Best Fit - LHS Fragmentation')
    else:
        axs[1].plot(next_bytes_requested, next_lhs_fragmentation, label="Next Fit - LHS Fragmentation", marker=',', color='red', linestyle="dotted")
        axs[1].set_ylabel('LHS Fragmentation')
    axs[1].set_xlabel('Bytes Requested')
    axs[1].set_title('LHS Fragmentation vs. Bytes Requested')
    axs[1].grid(True)
    axs[1].legend()

    # Plot for In-Between Fragmentation
    axs[2].plot(best_bytes_requested, best_in_between_fragmentation, label="Best Fit - In-Between Fragmentation", marker=',', color='green')
    if args.separate_axis:
        ax2 = axs[2].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - In-Between Fragmentation')
        ax2.plot(next_bytes_requested, next_in_between_fragmentation, label="Next Fit - In-Between Fragmentation", marker=',', color='green', linestyle="dotted")
        axs[2].set_ylabel('Best Fit - In-Between Fragmentation')
    else:
        axs[2].plot(next_bytes_requested, next_in_between_fragmentation, label="Next Fit - In-Between Fragmentation", marker=',', color='green', linestyle="dotted")
        axs[2].set_ylabel('In-Between Fragmentation')
    axs[2].set_xlabel('Bytes Requested')
    axs[2].set_title('In-Between Fragmentation vs. Bytes Requested')
    axs[2].grid(True)
    axs[2].legend()

    plt.tight_layout()
    makedirs(args.output_dir, exist_ok=True)
    if args.separate_axis:
        plt.savefig(Path(args.output_dir) / Path(f"SEP_{Path(args.best_fit_log_file).name.split('.')[-2]}.png"))
    else:
        plt.savefig(Path(args.output_dir) / Path(f"{Path(args.best_fit_log_file).name.split('.')[-2]}.png"))
    plt.show()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
            description="Process results from a single performance eval run. Plot the results"
            )

    parser.add_argument(
            "--best_fit_log_file",
            type=str,
            required=True,
            help="Path to the log file produced by the robot script, running the workload on CantripOS using Best Fit allocation strategy.",
            )

    parser.add_argument(
            "--next_fit_log_file",
            type=str,
            required=True,
            help="Path to the log file produced by the robot script, running the workload on CantripOS using Next Fit allocation strategy.",
            )
    parser.add_argument(
            "--output_dir",
            type=str,
            default="./plots/memory_profiles",
            help="Path pointing to dir in which the resulting plot will be saved.",
            )
    parser.add_argument(
            "--separate_axis",
            action="store_true",
            help="If set, will plot LHS and in-between fragmentation on separate axis, to see both Best fit and Next fit patterns if scale is too large.",
            )

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()

    best_data = process_lines_from_file(args.best_fit_log_file)
    next_data = process_lines_from_file(args.next_fit_log_file)
    print("plotting..")
    plot_metrics(best_data=best_data, next_data=next_data, args=args)


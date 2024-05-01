import matplotlib.pyplot as plt
import numpy as np
import json
import argparse
from pathlib import Path

def process_lines_from_file(file_path: str):
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

            if all(key in json_data for key in ["idx", "untyped_too_small", "oom", "lhs_fragmentation_per_slab", "in_between_fragmentation_per_slab", "occupied_memory_per_slab", "available_space_per_slab"]):
                print(json_data["idx"])
                if json_data['idx'] == 0:
                    # skip state for idx 0 - not interesting
                    continue
                data.append({
                    "idx": json_data["idx"],
                    "untyped_too_small": json_data["untyped_too_small"],
                    "oom": json_data["oom"],
                    "lhs_fragmentation_per_slab": json_data["lhs_fragmentation_per_slab"],
                    "in_between_fragmentation_per_slab": json_data["in_between_fragmentation_per_slab"],
                    "occupied_memory_per_slab": json_data["occupied_memory_per_slab"],
                    "available_space_per_slab": json_data["available_space_per_slab"],
                })
        except Exception as e:
            continue  # Skip lines that do not contain valid JSON data or have other issues

    return data

def plot_metrics(data, args: argparse.Namespace):
    # Plotting
    fig, axs = plt.subplots(4, figsize=(10, 15))

    bar_width = 0.5
    index = np.arange(len(data[0]["lhs_fragmentation_per_slab"]))

    for i, row in enumerate(data):
        (lhs, in_between, occupied, available) = row["lhs_fragmentation_per_slab"], row["in_between_fragmentation_per_slab"], row["occupied_memory_per_slab"], row["available_space_per_slab"]
        axs[i].bar(index, available, width=bar_width, label='available_space', color='tab:brown')
        axs[i].bar(index, occupied, width=bar_width, label='occupied_memory', color='tab:blue')
        axs[i].bar(index, lhs, width=bar_width, label='lhs_fragmentation', color='tab:red')
        axs[i].bar(index, in_between, bottom=lhs, width=bar_width, label='in_between_fragmentation', color='tab:orange')

        axs[i].set_title(f"Memory slab status after {data[i]['idx']} alloc/dealloc operations")
        axs[i].set_xlabel("Slab")
        axs[i].set_ylabel("Memory")
        axs[i].legend()

        axs[i].set_yscale('log', base=2)
        axs[i].set_xticks(index)
        axs[i].set_xticklabels(range(1, len(lhs)+1))
        print(f"Best fit: No. failed UntypedRetype invocations: {data[i]['untyped_too_small']}, Out of Memory thrown: {data[i]['oom']}")
    plt.tight_layout()
    plt.savefig(f"{Path(args.best_fit_log_file).name.split('.')[-2]}.png")
    plt.savefig('memory_state_random_alloc_1000_50_perc_chance_dealloc_seed_42.png')
    plt.show()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
            description="Process results for memory stats at 25th,50th,75th,100th percentiles for an eval run."
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
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    file_path_best_fit = args.best_fit_log_file
    file_path_next_fit = args.next_fit_log_file

    # TODO: also plot for next fit, next to best fit
    data = process_lines_from_file(file_path_best_fit)
    print("plotting...")
    plot_metrics(data, args)


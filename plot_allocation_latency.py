import json
import matplotlib.pyplot as plt
import matplotlib
import argparse
from pathlib import Path
from os import makedirs
import seaborn as sns
import numpy as np

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

            if all(key in json_data for key in ["bytes requested", "slab resets", "untyped_too_small", "oom", "bytes in-use", "instruction count", "allocation"]):
                data.append({
                    "bytes_requested": json_data["bytes requested"],
                    "slab_resets":  json_data["slab resets"],
                    "untyped_too_small":  json_data["untyped_too_small"],
                    "oom":  json_data["oom"],
                    "bytes_in_use": json_data["bytes in-use"],
                    "instruction_count": json_data["instruction count"],
                    "allocation": json_data["allocation"],
                })
        except Exception as e:
            continue  # Skip lines that do not contain valid JSON data or have other issues

    return data

def plot_metrics(best_data, next_data, args: argparse.Namespace):
    # Configure for PGF plots
    matplotlib.rcParams.update(
        {
            "pgf.texsystem": "pdflatex",
            "font.family": "serif",
            "text.usetex": True,
        }
    )
    matplotlib.use("pgf")
    # NOTE: Changing font scale can drastically change plot size!
    sns.set(style="whitegrid", font_scale=2)
    plt.rcParams.update(
    {
        "text.color": "black",
        "axes.edgecolor": "black",
        "axes.labelcolor": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "axes.linewidth": 1.5,
        "xtick.major.size": 5,
        "xtick.minor.size": 3,
        "ytick.major.size": 5,
        "ytick.minor.size": 3,
    }
    )
    # Extracting data for plotting
    best_bytes_requested = np.array([entry["bytes_requested"] for entry in best_data])
    best_slab_resets = np.array([entry["slab_resets"] for entry in best_data])
    best_oom = [entry["oom"] for entry in best_data]
    # process oom: mask of True where oom actually ocurred
    best_oom = np.diff(best_oom, prepend=0) > 0 # prepend a 0 to match dimension (if there was oom on first call, will also catch that)
    best_bytes_in_use = np.array([entry["bytes_in_use"] for entry in best_data])
    best_instruction_count = np.array([entry["instruction_count"] for entry in best_data])
    best_is_allocation = np.array([entry["allocation"] for entry in best_data])

    next_bytes_requested = np.array([entry["bytes_requested"] for entry in next_data])
    next_slab_resets = np.array([entry["slab_resets"] for entry in next_data])
    next_oom = [entry["oom"] for entry in next_data]
    # process oom: mask of True where oom actually ocurred
    next_oom = np.diff(next_oom, prepend=0) > 0 # prepend a 0 to match dimension (if there was oom on first call, will also catch that)
    next_bytes_in_use = np.array([entry["bytes_in_use"] for entry in next_data])
    next_instruction_count = np.array([entry["instruction_count"] for entry in next_data])
    next_is_allocation = np.array([entry["allocation"] for entry in next_data])

    # Creating separate plots for each metric
    fig, axs = plt.subplots(3, 1, figsize=(14, 21))

    # Plot for Bytes in Use
    axs[0].plot(best_bytes_requested, best_bytes_in_use, label="Best Fit - Bytes in Use", marker=',', color='blue', linewidth=3)
    axs[0].plot(next_bytes_requested, next_bytes_in_use, label="Next Fit - Bytes in Use", marker=',', color='blue', linestyle="dotted", linewidth=3)
    axs[0].set_ylabel('Bytes in Use')
    axs[0].set_xlabel('Bytes Requested')
    axs[0].set_title('Bytes in Use vs. Bytes Requested')
    axs[0].grid(True)

    # Plot for Allocation latency
    axs[1].plot(best_bytes_requested[best_is_allocation == True], best_instruction_count[best_is_allocation == True], label="Best Fit - Instruction Count per Allocation", marker=',', color='tab:brown', linewidth=3)
    if np.sum(best_oom) > 0: # only plot if there are points
        axs[1].scatter(best_bytes_requested[best_oom], best_instruction_count[best_oom], s=[225]*np.sum(best_oom), label="Best Fit - Out of Memory", marker='x', color="tab:red", linewidth=2)
    if args.separate_axis:
        ax2 = axs[1].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - Instruction Count per Alloc')
        ax2.plot(next_bytes_requested[next_is_allocation == True], next_instruction_count[next_is_allocation == True], label="Next Fit - Instruction Count per Allocation", marker=',', color='tab:brown', linestyle="dotted", linewidth=3)
        if np.sum(next_oom) > 0: # only plot if there are points
            ax2.scatter(next_bytes_requested[next_oom], next_instruction_count[next_oom], s=[225]*np.sum(next_oom), label="Next Fit - Out of Memory", marker='+', color="tab:red", linewidth=2)
        axs[1].set_ylabel('Best Fit - Instruction Count per Alloc')
    else:
        axs[1].plot(next_bytes_requested[next_is_allocation == True], next_instruction_count[next_is_allocation == True], label="Next Fit - Instruction Count per Allocation", marker=',', color='tab:purple', linestyle="dotted", linewidth=3)
        if np.sum(next_oom) > 0: # only plot if there are points
            axs[1].scatter(next_bytes_requested[next_oom], next_instruction_count[next_oom], s=[225]*np.sum(next_oom), label="Next Fit - Out of Memory", marker='+', color="tab:red", linewidth=2)
        axs[1].set_ylabel('Instruction Count per Alloc')
    axs[1].set_xlabel('Bytes Requested')
    axs[1].set_title('Instruction Count per Allocation vs. Bytes Requested')
    axs[1].grid(True)

    # Plot for Freeing latency (should be constant?)
    axs[2].plot(best_bytes_requested[best_is_allocation == False], best_instruction_count[best_is_allocation == False], label="Best Fit - Instruction count per Free", marker=',', color='tab:grey', linewidth=3)
    if args.separate_axis:
        ax2 = axs[2].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - Instruction Count per Free')
        ax2.plot(next_bytes_requested[next_is_allocation == False], next_instruction_count[next_is_allocation == False], label="Next Fit - Instruction Count per Free", marker=',', color='tab:orange', linestyle="dotted", linewidth=3)
        axs[2].set_ylabel('Best Fit - Instruction Count per Free')
    else:
        axs[2].plot(next_bytes_requested[next_is_allocation == False], next_instruction_count[next_is_allocation == False], label="Next Fit - Instruction Count per Free", marker=',', color='tab:orange', linestyle="dotted", linewidth=3)
        axs[2].set_ylabel('Instruction Count per Free')
    axs[2].set_xlabel('Bytes Requested')
    axs[2].set_title('Instruction Count per Free vs. Bytes Requested')
    axs[2].grid(True)

    # Merge all legends
    handles0, labels0 = axs[0].get_legend_handles_labels()
    handles1, labels1 = axs[1].get_legend_handles_labels()
    handles2, labels2 = axs[2].get_legend_handles_labels()
    #axs[0].set_yscale('log')#, base=2)
    axs[1].set_yscale('log')#, base=2)
    axs[2].set_yscale('log')#, base=2)
    plt.legend(
        handles0 + handles1 + handles2,
        labels0 + labels1 + labels2,
        loc="upper center",
        # to avoid cutting into the text
        borderpad=1,
        bbox_to_anchor=(0.5, -0.120),
        ncol=2,
        frameon=True,
        fancybox=True,
        edgecolor="black",
    )
    #axs[0].legend()
    #axs[1].legend()
    #axs[2].legend()

    plt.tight_layout()
    makedirs(args.output_dir, exist_ok=True)
    if args.separate_axis:
        plt.savefig(Path(args.output_dir) / Path(f"SEP_{Path(args.best_fit_log_file).name.split('.')[-2]}.png"))
    else:
        plt.savefig(Path(args.output_dir) / Path(f"{Path(args.best_fit_log_file).name.split('.')[-2]}.png"))
        plt.savefig(Path(args.output_dir) / Path(f"{Path(args.best_fit_log_file).name.split('.')[-2]}.pdf"), bbox_inches="tight")
    plt.show()
    print(f"Avg. latency Alloc: Best Fit: {np.sum(best_instruction_count[best_is_allocation == True]) / np.sum(best_is_allocation == True)}; Next Fit: {np.sum(next_instruction_count[next_is_allocation == True]) / np.sum(next_is_allocation == True)}")
    print(f"Avg. latency Free: Best Fit: {np.sum(best_instruction_count[best_is_allocation == False]) / np.sum(best_is_allocation == False)}; Next Fit: {np.sum(next_instruction_count[next_is_allocation == False]) / np.sum(next_is_allocation == False)}")
    print(f"Excluding latencies when OOM ocurred:")
    print("Avg. latency Alloc: Best Fit: ",
    np.sum(best_instruction_count[(best_is_allocation == True) & (best_oom != True)]) / np.sum((best_is_allocation == True) & (best_oom != True)),
    "; Next Fit: ",
    np.sum(next_instruction_count[(next_is_allocation == True) & (next_oom != True)]) / np.sum((next_is_allocation == True) & (next_oom != True)))
    print(f"Avg. latency Free: Best Fit: ",
    np.sum(best_instruction_count[(best_is_allocation == False) & (best_oom != True)]) / np.sum((best_is_allocation == False) & (best_oom != True)),
    f"; Next Fit: {np.sum(next_instruction_count[(next_is_allocation == False) & (next_oom != True)]) / np.sum((next_is_allocation == False) & (next_oom != True))}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
            description="Process results from a single latency eval run. Plot the results"
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


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
        except StopIteration:
            print("Not a sequential application workload, checking if concurrent sequential application workload")
            begin_line_index = next(i for i, line in enumerate(lines) if "replay_concurr_app" in line)
    
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

            if all(key in json_data for key in ["bytes in-use", "slab resets", "untyped_too_small", "oom", "bytes free", "bytes requested", "lhs fragmentation", "in-between fragmentation"]):
                data.append({
                    "bytes_in_use": json_data["bytes in-use"],
                    "slab_resets":  json_data["slab resets"],
                    "untyped_too_small":  json_data["untyped_too_small"],
                    "oom":  json_data["oom"],
                    "bytes_free": json_data["bytes free"],
                    "bytes_requested": json_data["bytes requested"],
                    "lhs_fragmentation": json_data["lhs fragmentation"],
                    "in_between_fragmentation": json_data["in-between fragmentation"],
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
    best_lhs_fragmentation = np.array([entry["lhs_fragmentation"] for entry in best_data])
    best_in_between_fragmentation = np.array([entry["in_between_fragmentation"] for entry in best_data])

    next_bytes_requested = np.array([entry["bytes_requested"] for entry in next_data])
    next_slab_resets = np.array([entry["slab_resets"] for entry in next_data])
    next_oom = [entry["oom"] for entry in next_data]
    # process oom: mask of True where oom actually ocurred
    next_oom = np.diff(next_oom, prepend=0) > 0 # prepend a 0 to match dimension (if there was oom on first call, will also catch that)
    next_bytes_in_use = np.array([entry["bytes_in_use"] for entry in next_data])
    next_lhs_fragmentation = np.array([entry["lhs_fragmentation"] for entry in next_data])
    next_in_between_fragmentation = np.array([entry["in_between_fragmentation"] for entry in next_data])

    # Creating separate plots for each metric
    fig, axs = plt.subplots(3, 1, figsize=(14, 21))

    # Plot for Bytes in Use
    axs[0].plot(best_bytes_requested, best_bytes_in_use, label="Best Fit - Bytes in Use", marker=',', color='blue', linewidth=3)
    axs[0].plot(next_bytes_requested, next_bytes_in_use, label="Next Fit - Bytes in Use", marker=',', color='blue', linestyle="dotted", linewidth=3)
    axs[0].set_ylabel('Bytes in Use')
    axs[0].set_xlabel('Bytes Requested')
    axs[0].set_title('Bytes in Use vs. Bytes Requested')
    # Plot slab resets on same graph, marking OOM for both Best and next fit
    ax02 = axs[0].twinx()
    ax02.tick_params(axis="y", labelcolor="tab:blue")
    ax02.plot(best_bytes_requested, best_slab_resets, label="Best Fit - Slab Resets", marker=',', color="tab:orange", alpha=0.6, linewidth=3)
    ax02.plot(next_bytes_requested, next_slab_resets, label="Next Fit - Slab Resets", marker=',', color="tab:orange", alpha=0.6, linestyle="dotted", linewidth=3)
    # Mark OOM, s=[81] is the size for each marker (its area)
    if np.sum(best_oom) > 0: # only plot if there are points
        ax02.scatter(best_bytes_requested[best_oom], best_slab_resets[best_oom], s=[225]*np.sum(best_oom), label="Best Fit - Out of Memory", marker='x', color="tab:red", linewidth=2)
    if np.sum(next_oom) > 0: # only plot if there are points
        ax02.scatter(next_bytes_requested[next_oom], next_slab_resets[next_oom], s=[225]*np.sum(next_oom), label="Next Fit - Out of Memory", marker='+', color="tab:red", linewidth=2)
    ax02.set_ylabel("Slab reset count")
    axs[0].grid(True)
    ax02.grid(False)#, which='both', zorder = axs[0].get_zorder() -1)

    # Plot for Watermarking Cons. Fragmentation
    axs[1].plot(best_bytes_requested, best_lhs_fragmentation, label="Best Fit - Watermarking Con. Fragmentation", marker=',', color='red', linewidth=3)
    if args.separate_axis:
        ax2 = axs[1].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - Watermarking Cons. Fragmentation')
        ax2.plot(next_bytes_requested, next_lhs_fragmentation, label="Next Fit - Watermarking Con. Fragmentation", marker=',', color='red', linestyle="dotted", linewidth=3)
        axs[1].set_ylabel('Best Fit - Watermarking Cons. Fragmentation')
    else:
        axs[1].plot(next_bytes_requested, next_lhs_fragmentation, label="Next Fit - Watermarking Con. Fragmentation", marker=',', color='red', linestyle="dotted", linewidth=3)
        axs[1].set_ylabel('Watermarking Cons. Fragmentation')
    axs[1].set_xlabel('Bytes Requested')
    axs[1].set_title('Watermarking Cons. Fragmentation vs. Bytes Requested')
    axs[1].grid(True)

    # Plot for Alignment Cons. Fragmentation
    axs[2].plot(best_bytes_requested, best_in_between_fragmentation, label="Best Fit - Alignment Con. Fragmentation", marker=',', color='green', linewidth=3)
    if args.separate_axis:
        ax2 = axs[2].twinx()
        color="tab:blue"
        ax2.tick_params(axis="y", labelcolor=color)
        ax2.set_ylabel('Next Fit - Alignment Cons. Fragmentation')
        ax2.plot(next_bytes_requested, next_in_between_fragmentation, label="Next Fit - Alignment Con. Fragmentation", marker=',', color='green', linestyle="dotted", linewidth=3)
        axs[2].set_ylabel('Best Fit - Alignment Cons. Fragmentation')
    else:
        axs[2].plot(next_bytes_requested, next_in_between_fragmentation, label="Next Fit - Alignment Con. Fragmentation", marker=',', color='green', linestyle="dotted", linewidth=3)
        axs[2].set_ylabel('Alignment Cons. Fragmentation')
    axs[2].set_xlabel('Bytes Requested')
    axs[2].set_title('Alignment Cons. Fragmentation vs. Bytes Requested')
    axs[2].grid(True)

    # Merge all legends
    handles0, labels0 = axs[0].get_legend_handles_labels()
    handles02, labels02 = ax02.get_legend_handles_labels()
    handles1, labels1 = axs[1].get_legend_handles_labels()
    handles2, labels2 = axs[2].get_legend_handles_labels()
    axs[2].legend(
        handles0 + handles02 + handles1 + handles2,
        labels0 + labels02 + labels1 + labels2,
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


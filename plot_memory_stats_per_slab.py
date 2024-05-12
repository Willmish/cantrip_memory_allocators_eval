import matplotlib.pyplot as plt
import numpy as np
import json
import argparse
from pathlib import Path
from os import makedirs

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

            if all(key in json_data for key in ["idx", "slab_resets", "untyped_too_small", "oom", "lhs_fragmentation_per_slab", "in_between_fragmentation_per_slab", "occupied_memory_per_slab", "available_space_per_slab"]):
                print(json_data["idx"])
                if json_data['idx'] == 0:
                    # skip state for idx 0 - not interesting
                    continue
                data.append({
                    "idx": json_data["idx"],
                    "slab_resets": json_data["slab_resets"],
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

def plot_metrics(best_data, next_data, args: argparse.Namespace):
    # Plotting
    fig, axs = plt.subplots(4, figsize=(10, 15))

    bar_width = 0.4
    patterns = ['', 'XX']
    next_fit_alpha = 0.8
    metrics = ["available_space_per_slab", "occupied_memory_per_slab", "in_between_fragmentation_per_slab", "lhs_fragmentation_per_slab"]
    colors = ["tab:brown", "tab:blue", "tab:orange", "tab:red"]
    plot_titles = ["Available space", "Used memory", "Alignment cons. fragmentation", "Watermarking cons. fragmentation"]

    index = np.arange(len(best_data[0]["lhs_fragmentation_per_slab"]))

    for i in range(4):
        row_best, row_next = best_data[i], next_data[i]
        print(row_best)
        print(row_next)
        for metric_idx, metric in enumerate(metrics):
            if metric == 'in_between_fragmentation_per_slab':
                axs[i].bar(index-bar_width/2, row_best[metric], bottom=row_best["lhs_fragmentation_per_slab"] , width=bar_width, label=f"Best Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[0])
                axs[i].bar(index+bar_width/2, row_next[metric], bottom=row_next["lhs_fragmentation_per_slab"], width=bar_width, label=f"Next Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[1], alpha=next_fit_alpha)
            else:
                axs[i].bar(index-bar_width/2, row_best[metric], width=bar_width, label=f"Best Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[0])
                axs[i].bar(index+bar_width/2, row_next[metric], width=bar_width, label=f"Next Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[1], alpha=next_fit_alpha)
        axs[i].set_title(f"Memory slab status after {best_data[i]['idx']} alloc/dealloc operations")
        axs[i].set_xlabel("Slab")
        axs[i].set_ylabel("Memory")

        #axs[i].set_yscale('log', base=2)
        axs[i].set_xticks(index)
        axs[i].set_xticklabels(range(1, len(row_best[metrics[0]])+1))

        # Add zoomed-in inset
        zoom_start_idx = 14
        zoom_end_idx = 21
        zoom_start_y = 0
        zoom_end_y = 17500#35000
        zoom_indices = index[zoom_start_idx:]
        axins = axs[i].inset_axes(
            [0.5, 0.4, 0.47, 0.47], # x, y, width, height as fractions of parent's bbox
            #65536
            xlim=(zoom_start_idx+0.5, zoom_end_idx + 0.5),
            ylim=(zoom_start_y,zoom_end_y),
            xticklabels=[],
            yticklabels=[],
        )  
        for metric_idx, metric in enumerate(metrics):
            if metric == 'in_between_fragmentation_per_slab':
                axins.bar(zoom_indices-bar_width/2, row_best[metric][zoom_start_idx:], bottom=row_best["lhs_fragmentation_per_slab"][zoom_start_idx:] , width=bar_width, label=f"Best Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[0])
                axins.bar(zoom_indices+bar_width/2, row_next[metric][zoom_start_idx:], bottom=row_next["lhs_fragmentation_per_slab"][zoom_start_idx:], width=bar_width, label=f"Next Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[1], alpha=next_fit_alpha)
            else:
                axins.bar(zoom_indices-bar_width/2, row_best[metric][zoom_start_idx:], width=bar_width, label=f"Best Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[0])
                axins.bar(zoom_indices+bar_width/2, row_next[metric][zoom_start_idx:], width=bar_width, label=f"Next Fit - {plot_titles[metric_idx]}", color=colors[metric_idx], hatch=patterns[1], alpha=next_fit_alpha)

        axins.set_xticklabels(range(zoom_start_idx+1, zoom_end_idx+2))
        axins.set_yticks(np.linspace(0, zoom_end_y, num=5))
        axins.set_yticklabels(np.linspace(0, zoom_end_y, num=5, dtype=int))

        axs[i].indicate_inset_zoom(axins, edgecolor="black")

        print(f"Best fit: Slab resets: {best_data[i]['slab_resets']} No. failed UntypedRetype invocations: {best_data[i]['untyped_too_small']}, Out of Memory thrown: {best_data[i]['oom']}")
        print(f"Next fit: Slab resets: {next_data[i]['slab_resets']} No. failed UntypedRetype invocations: {next_data[i]['untyped_too_small']}, Out of Memory thrown: {next_data[i]['oom']}")
    axs[3].legend(loc="upper center",
        # to avoid cutting into the text
        borderpad=1,
        bbox_to_anchor=(0.5, -0.130),
        ncol=2,
        frameon=True,
        fancybox=True,
        edgecolor="black",
        )
    plt.tight_layout()
    makedirs(args.output_dir, exist_ok=True)
    plt.savefig(Path(args.output_dir) / Path(f"{Path(args.best_fit_log_file).name.split('.')[-2]}.png"))
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
    parser.add_argument(
            "--output_dir",
            type=str,
            default="./plots/memory_stats",
            help="Path pointing to dir in which the resulting plot will be saved.",
            )
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    file_path_best_fit = args.best_fit_log_file
    file_path_next_fit = args.next_fit_log_file

    # TODO: also plot for next fit, next to best fit
    best_data = process_lines_from_file(file_path_best_fit)
    next_data = process_lines_from_file(file_path_next_fit)
    print("plotting...")
    plot_metrics(best_data=best_data, next_data=next_data, args=args)


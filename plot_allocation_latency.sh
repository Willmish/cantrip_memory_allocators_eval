#!/bin/bash
# Calls a Python script with an equivalent name, to plot all memory usage plots.

# Requires python environment with matplotlib and numpy

echo "Plotting synthetic workload run results: Random Uniform.."
OUTPUT_DIR="./plots/memory_profiles/random_uniform"
python3 plot_allocation_latency.py --best_fit_log_file best_fit/random_uniform/latency_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_16.log --next_fit_log_file next_fit/random_uniform/latency_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_16.log --output_dir $OUTPUT_DIR

python3 plot_allocation_latency.py --best_fit_log_file best_fit/random_uniform/latency_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_32.log --next_fit_log_file next_fit/random_uniform/latency_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_32.log --output_dir $OUTPUT_DIR

python3 plot_allocation_latency.py --best_fit_log_file best_fit/random_uniform/latency_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_48.log --next_fit_log_file next_fit/random_uniform/latency_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_48.log --output_dir $OUTPUT_DIR

python3 plot_allocation_latency.py --best_fit_log_file best_fit/random_uniform/latency_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_64.log --next_fit_log_file next_fit/random_uniform/latency_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_64.log --output_dir $OUTPUT_DIR


#echo "Plotting synthetic workload (SEPARATE AXIS) run results: Random Uniform.."
#OUTPUT_DIR="./plots/memory_profiles/random_uniform"
#python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_16.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_16.log --output_dir $OUTPUT_DIR --separate_axis
#
#python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_32.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_32.log --output_dir $OUTPUT_DIR --separate_axis
#
#python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_48.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_48.log --output_dir $OUTPUT_DIR --separate_axis
#
#python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_64.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_64.log --output_dir $OUTPUT_DIR --separate_axis

echo "Done :)"

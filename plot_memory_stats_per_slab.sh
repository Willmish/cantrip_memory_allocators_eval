#!/bin/bash
# Calls a Python script with an equivalent name, to plot all memory stats plots.

# Requires python environment with matplotlib and numpy
#
python3 plot_memory_stats_per_slab.py --best_fit_log_file best_fit/random_uniform/memory_stats_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_16.log --next_fit_log_file next_fit/random_uniform/memory_stats_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_16.log

python3 plot_memory_stats_per_slab.py --best_fit_log_file best_fit/random_uniform/memory_stats_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_32.log --next_fit_log_file next_fit/random_uniform/memory_stats_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_32.log

python3 plot_memory_stats_per_slab.py --best_fit_log_file best_fit/random_uniform/memory_stats_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_48.log --next_fit_log_file next_fit/random_uniform/memory_stats_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_48.log

python3 plot_memory_stats_per_slab.py --best_fit_log_file best_fit/random_uniform/memory_stats_random_uniform_best_fit_seed_42_count_1000_dealloc_chance_64.log --next_fit_log_file next_fit/random_uniform/memory_stats_random_uniform_next_fit_seed_42_count_1000_dealloc_chance_64.log

echo "Done :)"

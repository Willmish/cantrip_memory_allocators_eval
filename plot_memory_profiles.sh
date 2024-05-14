#!/bin/bash
# Calls a Python script with an equivalent name, to plot all memory usage plots.

# Requires python environment with matplotlib and numpy

echo "Plotting synthetic workload run results: Random Uniform.."
OUTPUT_DIR="./plots/memory_profiles/random_uniform"
python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_16.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_16.log --output_dir $OUTPUT_DIR

python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_32.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_32.log --output_dir $OUTPUT_DIR

python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_48.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_48.log --output_dir $OUTPUT_DIR

python3 plot_memory_profiles.py --best_fit_log_file best_fit/random_uniform/random_uniform_best_fit_seed_42_count_1000_dealloc_chance_64.log --next_fit_log_file next_fit/random_uniform/random_uniform_next_fit_seed_42_count_1000_dealloc_chance_64.log --output_dir $OUTPUT_DIR

echo "Plotting realistic workload run results: Standalone Application profiles.."
OUTPUT_DIR="./plots/memory_profiles/applications_standalone"
APP_NAMES=(hello timer mltest fibonacci)

for app in ${APP_NAMES[@]}
do
    echo "App: $app"
    python3 plot_memory_profiles.py --best_fit_log_file best_fit/apps_standalone/apps_standalone_best_fit_app_name_$app.log --next_fit_log_file next_fit/apps_standalone/apps_standalone_next_fit_app_name_$app.log --output_dir $OUTPUT_DIR
done

echo "Plotting realistic workload run results: Sequential Application profiles.."
OUTPUT_DIR="./plots/memory_profiles/applications_sequential"
# Sequence 1: # 4 ramps/spiking
# Sequence 2: # single large ramp
# Sequence 3: # 3 start, 2 stop, 1 start, 2 stop
SEQUENCE_NAMES=(1 2 3)

for seq in ${SEQUENCE_NAMES[@]}
do
    echo "Sequence: $seq"
    python3 plot_memory_profiles.py --best_fit_log_file best_fit/apps_sequential/apps_sequential_best_fit_sequence_$seq.log --next_fit_log_file next_fit/apps_sequential/apps_sequential_next_fit_sequence_$seq.log --output_dir $OUTPUT_DIR
done


echo "Done :)"

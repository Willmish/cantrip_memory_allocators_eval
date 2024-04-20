import matplotlib.pyplot as plt
import numpy as np
import json

# JSON data
data = [{'idx': 250, 'lhs_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4096, 0, 1024, 0, 0, 0, 0, 320], 'in_between_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3072, 0, 0, 0, 0, 176], 'occupied_memory_per_slab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16384, 0, 8192, 0, 512, 512, 528, 512], 'available_space_per_slab': [524288, 524288, 262144, 262144, 262144, 262144, 131072, 131072, 131072, 65536, 65536, 65536, 32768, 16384, 8192, 8192, 4096, 4096, 2048, 1024, 512]},
{'idx': 500, 'lhs_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12288, 4096, 0, 0, 2864, 1024, 512, 0], 'in_between_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 736, 512, 0, 0], 'occupied_memory_per_slab': [0, 0, 0, 0, 0, 0, 0, 0, 0, 53248, 0, 0, 32768, 16384, 8192, 8192, 4096, 3664, 2048, 1024, 512], 'available_space_per_slab': [524288, 524288, 262144, 262144, 262144, 262144, 131072, 131072, 131072, 65536, 65536, 65536, 32768, 16384, 8192, 8192, 4096, 4096, 2048, 1024, 512]},
{'idx': 750, 'lhs_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 57344, 0, 0, 32128, 0, 61440, 8192, 12288, 4096, 4096, 0, 496, 512, 704, 400], 'in_between_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 3072, 0, 0, 624, 0, 0, 4064, 0, 0, 0, 0, 1232, 240, 160, 48], 'occupied_memory_per_slab': [0, 0, 0, 0, 0, 0, 126976, 0, 0, 65536, 0, 65536, 32768, 16384, 8192, 8192, 4096, 4096, 1440, 1024, 512], 'available_space_per_slab': [524288, 524288, 262144, 262144, 262144, 262144, 131072, 131072, 131072, 65536, 65536, 65536, 32768, 16384, 8192, 8192, 4096, 4096, 2048, 1024, 512]},
{'idx': 1000, 'lhs_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 122512, 95744, 50992, 0, 8208, 63504, 0, 12112, 512, 0, 0, 592, 1488, 624, 416], 'in_between_fragmentation_per_slab': [0, 0, 0, 0, 0, 0, 4464, 13824, 13488, 0, 9632, 1504, 0, 3248, 3584, 0, 0, 1424, 304, 128, 48], 'occupied_memory_per_slab': [0, 0, 0, 0, 0, 0, 131072, 131072, 131072, 0, 49152, 65536, 32768, 16384, 8192, 8192, 128, 4096, 2048, 1024, 512], 'available_space_per_slab': [524288, 524288, 262144, 262144, 262144, 262144, 131072, 131072, 131072, 65536, 65536, 65536, 32768, 16384, 8192, 8192, 4096, 4096, 2048, 1024, 512]}]
# Extracting data for plotting
idxs = []
lhs_fragmentation = []
in_between_fragmentation = []
occupied_memory = []
available_space = []

for i, d in enumerate(data):
    idxs.append(d['idx'])
    lhs_fragmentation.append(d['lhs_fragmentation_per_slab'])
    print(len(d['lhs_fragmentation_per_slab']))
    in_between_fragmentation.append(d['in_between_fragmentation_per_slab'])
    print(len(d['in_between_fragmentation_per_slab']))
    occupied_memory.append(d['occupied_memory_per_slab'])
    print(len(d['occupied_memory_per_slab']))
    available_space.append(d['available_space_per_slab'])
    print(len(d['available_space_per_slab']))

# Plotting
fig, axs = plt.subplots(4, figsize=(10, 15))

bar_width = 0.2
index = np.arange(len(lhs_fragmentation[0]))

for i, (lhs, in_between, occupied, available) in enumerate(zip(lhs_fragmentation, in_between_fragmentation, occupied_memory, available_space)):
    axs[i].bar(index - 2 * bar_width, available, width=bar_width, label='available_space')
    axs[i].bar(index - bar_width, occupied, width=bar_width, label='occupied_memory')
    axs[i].bar(index, lhs, width=bar_width, label='lhs_fragmentation')
    axs[i].bar(index + bar_width, in_between, width=bar_width, label='in_between_fragmentation')

    axs[i].set_title(f"Memory slab status after {idxs[i]} alloc/dealloc operations")
    axs[i].set_xlabel("Slab")
    axs[i].set_ylabel("Memory")
    axs[i].legend()

    axs[i].set_xticks(index)
    axs[i].set_xticklabels(range(1, len(lhs)+1))
## Plotting
#fig, axs = plt.subplots(4, figsize=(10, 15))
#
#for i, (lhs, in_between, occupied, available) in enumerate(zip(lhs_fragmentation, in_between_fragmentation, occupied_memory, available_space)):
#    axs[i].bar(range(len(lhs)), lhs, label='lhs_fragmentation')
#    axs[i].bar(range(len(in_between)), in_between, bottom=lhs, label='in_between_fragmentation')
#    axs[i].bar(range(len(occupied)), occupied, bottom=[lhs[j] + in_between[j] for j in range(len(lhs))], label='occupied_memory')
#    axs[i].bar(range(len(available)), available, bottom=[lhs[j] + in_between[j] + occupied[j] for j in range(len(lhs))], label='available_space')
#
#    axs[i].set_title(f"Memory state at {idxs[i]} alloc/dealloc operations")
#    axs[i].set_xlabel("Slab")
#    axs[i].set_ylabel("Memory")
#    axs[i].legend()

plt.tight_layout()
plt.savefig('memory_state_random_alloc_1000_50_perc_chance_dealloc_seed_42.png')
plt.show()


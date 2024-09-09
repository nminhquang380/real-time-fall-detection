import os
from generate_picture import generate_pic

def get_all_files(dir_path):
    file_list = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

base_dir = 'C:/Users/T590/Desktop/ImageGeneration/ImageGeneration/sample_raw_radar_dataset_without_image'

# Recursively traverse all files in the directory and subdirectories
file_list = get_all_files(base_dir)

# Filter files based on whether the filename contains "I_raw"
filtered_files = [f for f in file_list if 'I_raw' in os.path.basename(f)]

# Remove the characters after the last backslash (\) in each file path
filtered_files = [os.path.dirname(f) for f in filtered_files]

print("Files with 'I_raw' in their names:")
print(filtered_files)

for current_file in filtered_files:
    generate_pic(current_file)

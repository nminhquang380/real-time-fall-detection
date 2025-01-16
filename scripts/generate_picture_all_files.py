import os
import shutil
from generate_picture import generate_pic
import argparse

parser = argparse.ArgumentParser(description="LearnToPayAttn-CT2D")
parser.add_argument('--input', type=str, required=True, help='Path to the input directory')
parser.add_argument('--output', type=str, required=True, help='Path to the output directory')

args = parser.parse_args()


def get_all_files(dir_path):
    file_list = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def generate_pic_all_files(base_dir=args.input, des_dir=args.output):
    # Recursively traverse all files in the directory and subdirectories
    file_list = get_all_files(base_dir)

    # Filter files based on whether the filename contains "I_raw"
    filtered_files = [f for f in file_list if 'I_raw' in os.path.basename(f)]

    # Remove the characters after the last backslash (\) in each file path
    filtered_files = [os.path.dirname(f) for f in filtered_files]

    print("Files with 'I_raw' in their names:")
    print(filtered_files)

    for current_file in filtered_files:
        generate_pic(current_file, des_dir)
        
if __name__ == "__main__":
    # base_dir = r'data\raw_signal_data'
    # destination_dir = r'data\image_data\quang'
    # generate_pic_all_files(base_dir, destination_dir)
    generate_pic_all_files()
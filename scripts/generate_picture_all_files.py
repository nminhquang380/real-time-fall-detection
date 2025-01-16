import os
import shutil
from generate_picture import generate_pic
from generate_picture_refactored import ImageGenerator
import argparse

parser = argparse.ArgumentParser(description="LearnToPayAttn-CT2D")
parser.add_argument('--input', type=str, required=True, help='Path to the input directory')
parser.add_argument('--output', type=str, required=True, help='Path to the output directory')

args = parser.parse_args()

def get_subfolders(dir_path):
    """
    Get a list of all subfolder paths in the base directory.
    """
    subfolders = [os.path.join(dir_path, d) for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
    return subfolders

def generate_pic_all_files(base_dir=args.input, des_dir=args.output):
    """
    Traverse subfolders in the base directory, create corresponding subfolders in the destination,
    and generate images for each subfolder.
    """
    # Get all subfolders in the base directory
    subfolders = get_subfolders(base_dir)

    for subfolder in subfolders:
            # Extract the subfolder name
            subfolder_name = os.path.basename(subfolder)

            # Create the corresponding subfolder in the destination directory
            output_subfolder = os.path.join(des_dir, subfolder_name)
            os.makedirs(output_subfolder, exist_ok=True)

            print(f"Processing: {subfolder} -> {output_subfolder}")

            # Call the generate_picture function for the current subfolder
            generate_pic(subfolder, output_subfolder)
        
if __name__ == "__main__":
    # base_dir = r'data\raw_signal_data'
    # destination_dir = r'data\image_data\quang'
    generate_pic_all_files()
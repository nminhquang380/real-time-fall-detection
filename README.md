# Image Generation Repository

This repository contains tools to generate images from signal data. The repository is organized into two main folders: `matlab` and `scripts`.

## Folders

### matlab
This folder contains MATLAB scripts for generating images from signal data.

### scripts
This folder contains Python scripts for generating images from signal data.

## Usage

To generate images using the Python script, run the following command:

```bash
python scripts/generate_picture_all_files.py --input folder_input --output folder_output
```

Replace `folder_input` with the path to your input folder containing signal data, and `folder_output` with the path to your desired output folder for the generated images.

## Requirements

- Python 3.x
- MATLAB (for MATLAB scripts)

## Installation

1. Navigate to the repository directory:
	```bash
	cd ImageGeneration
	```
2. Install the required Python packages:
	```bash
	pip install -r requirements.txt
	```

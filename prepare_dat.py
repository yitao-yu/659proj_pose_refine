from utils import *
import os

if __name__ == "__main__":
    fnames = [f for f in os.listdir('./bike/images/')]

    transforms = generate_transforms_json(
        images_file = './bike/sfm/images.txt',
        cameras_file = './bike/sfm/cameras.txt',
        output_file = './bike/transforms.json',
        fnames = fnames
    )

    # Sanity check
    assert len([frame['file_path'] for frame in transforms['frames']]) == len(fnames)
import json
import numpy as np

def quaternion_to_rotation_matrix(qw, qx, qy, qz):
    '''Convert quaternion to 3x3 rotation matrix.'''
    R = np.array([
        [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
        [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
        [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
    ])
    return R

def generate_transforms_json(images_file, cameras_file, output_file, fnames = None):
  # Load camera intrinsics from cameras.txt
  camera_intrinsics = {}
  with open(cameras_file, 'r') as cam_file:
    for line in cam_file:
      if line.startswith('#') or not line.strip():
        continue
      camera_id, model, width, height, *params = line.split()
      fx = float(params[0])
      cx = float(params[1])
      cy = float(params[2])
      k1 = float(params[3])
      camera_intrinsics[camera_id] = (float(width), float(height), fx, cx, cy, k1)

  # Create the transforms.json structure
  transforms = {
    "camera_model": "SIMPLE_RADIAL", 
    "frames": []
  }

  with open(images_file, 'r') as img_file:
    for line in img_file:
      # skip first few lines and empty strings
      if line.startswith('#') or not line.strip():
        continue
      # skip 2d points lines
      if len(line.split(" ")[0].split("."))>1:
        continue


      parts = line.split()
      image_id, qw, qx, qy, qz, tx, ty, tz, camera_id, name = parts[:10]

      # if fnames is not None, skip when images is not available
      if fnames is not None:
        if name not in fnames:
          continue

      # Get camera intrinsics for the current camera_id
      width, height, fx, cx, cy, k1 = camera_intrinsics[camera_id]

    #   # Compute horizontal FOV (camera_angle_x) if not set
    #   if transforms["camera_angle_x"] is None:
    #       transforms["camera_angle_x"] = 2 * np.arctan(width / (2 * fx))

      # Convert quaternion to rotation matrix
      rotation_matrix = quaternion_to_rotation_matrix(float(qw), float(qx), float(qy), float(qz))

      # Create the 4x4 transformation matrix [[R t],[0 1]]_4x4
      transform_matrix = np.eye(4)
      transform_matrix[:3, :3] = rotation_matrix
      transform_matrix[:3, 3] = [float(tx), float(ty), float(tz)]

      # Append frame data
      transforms["frames"].append({
          "file_path": f"images/{name}",
          "w":height,
          "h":width,
          "fl_x":fx,
          "fl_y":fx,
          "cx":cx,
          "cy":cy,
          "k1":k1,
          "transform_matrix": transform_matrix.tolist()
      })

  # Save to JSON file
  with open(output_file, 'w') as outfile:
      json.dump(transforms, outfile, indent=4)
  return transforms
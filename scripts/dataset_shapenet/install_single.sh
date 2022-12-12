source dataset_shapenet/config.sh

# Function for processing a single model
reorganize() {
  modelname="$3"
  output_path="$2/$modelname"
  build_path="$1"

  points_file="$build_path/4_points/$modelname.npz"
  points_out_file="$output_path/points.npz"

  pointcloud_file="$build_path/4_pointcloud/$modelname.npz"
  pointcloud_out_file="$output_path/pointcloud.npz"

  vox_file="$build_path/4_voxel/$modelname.binvox"
  vox_out_file="$output_path/model.binvox"

  echo "Copying model $output_path"
  mkdir -p "$output_path"

  cp "$points_file" "$points_out_file"
  cp "$pointcloud_file" "$pointcloud_out_file"
  cp "$vox_file" "$vox_out_file"
}

export -f reorganize

# Make output directories
mkdir -p "$OUTPUT_PATH"

SYNTHSET="$1"
HASH="$2"

# Run build
echo "Processing instance $HASH of class $SYNTHSET"
BUILD_PATH_C="$BUILD_PATH/$SYNTHSET"
OUTPUT_PATH_C="$OUTPUT_PATH/$SYNTHSET"
mkdir -p "$OUTPUT_PATH_C"

echo "Copying files"
reorganize "$BUILD_PATH_C" "$OUTPUT_PATH_C" "$HASH"

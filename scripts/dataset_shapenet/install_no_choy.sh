source dataset_shapenet/config.sh

# Function for processing a single model
reorganize() {
  modelname="$(basename -- $3)"
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

# Run build
for c in "${CLASSES[@]}"
do
  echo "Parsing class $c"
  INPUT_PATH_C="$INPUT_PATH/$c"
  BUILD_PATH_C="$BUILD_PATH/$c"
  OUTPUT_PATH_C="$OUTPUT_PATH/$c"
  mkdir -p "$OUTPUT_PATH_C"

  echo "Copying files"
  ls "$INPUT_PATH_C" | parallel -P "$NPROC" --timeout "$TIMEOUT" reorganize "$BUILD_PATH_C" "$OUTPUT_PATH_C" {}

  echo "Creating split"
  python create_split.py "$OUTPUT_PATH_C" --r_val 0.1 --r_test 0.2
done

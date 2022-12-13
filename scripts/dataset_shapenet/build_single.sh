source dataset_shapenet/config.sh
# Make output directories
mkdir -p "$BUILD_PATH"

SYNTHSET="$1"
HASH="$2"

# Run build
echo "Processing instance $HASH of class $SYNTHSET"
input_path_c="$INPUT_PATH/$SYNTHSET"
build_path_c="$BUILD_PATH/$SYNTHSET"

mkdir -p "$build_path_c"/0_in \
  "$build_path_c"/1_scaled \
  "$build_path_c"/2_depth \
  "$build_path_c"/2_watertight \
  "$build_path_c"/3_watertight_clean \
  "$build_path_c"/3_watertight_clean_simple \
  "$build_path_c"/4_points \
  "$build_path_c"/4_pointcloud \
  "$build_path_c"/4_voxel \
  "$build_path_c"/4_mesh

echo "Converting meshes to OFF"
meshlabserver -i "$input_path_c/$HASH/$MODEL_NAME" -o "$build_path_c/0_in/$HASH.off"

echo "Scaling meshes"
python "$MESHFUSION_PATH"/1_scale.py \
  --in_dir "$build_path_c"/0_in \
  --out_dir "$build_path_c"/1_scaled \
  --t_dir "$build_path_c"/1_transform \
  --overwrite

echo "Create depths maps"
python "$MESHFUSION_PATH"/2_fusion.py \
  --mode=render \
  --in_dir "$build_path_c"/1_scaled \
  --out_dir "$build_path_c"/2_depth \
  --overwrite

echo "Produce watertight meshes"
python "$MESHFUSION_PATH"/2_fusion.py \
  --mode=fuse \
  --in_dir "$build_path_c"/2_depth \
  --out_dir "$build_path_c"/2_watertight \
  --t_dir "$build_path_c"/1_transform \
  --overwrite

  echo "Clean watertight meshes"
  python "$MESHFUSION_PATH"/clean.py \
    --in_dir "$build_path_c"/2_watertight \
    --out_dir "$build_path_c"/3_watertight_clean \
    --overwrite

echo "Simplify watertight meshes"
  meshlabserver -i "$build_path_c/3_watertight_clean/$HASH.off" -o "$build_path_c/3_watertight_clean_simple/$HASH.off" -s "$MESHFUSION_PATH"/simplify.mlx

echo "Process watertight meshes"
python sample_mesh.py "$build_path_c"/3_watertight_clean_simple \
  --bbox_in_folder "$build_path_c"/0_in \
  --pointcloud_folder "$build_path_c"/4_pointcloud \
  --points_folder "$build_path_c"/4_points \
  --mesh_folder "$build_path_c"/4_mesh \
  --voxels_folder "$build_path_c"/4_voxel \
  --resize \
  --packbits \
  --float16 \
  --overwrite

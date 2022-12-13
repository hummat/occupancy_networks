source dataset_shapenet/config.sh
# Make output directories
mkdir -p "$BUILD_PATH"

# Run build
for c in "${CLASSES[@]}"
do
  echo "Processing class $c"
  input_path_c=$INPUT_PATH/$c
  build_path_c=$BUILD_PATH/$c

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
  # lsfilter "$input_path_c" "$build_path_c"/0_in .off | parallel -P "$NPROC" --timeout "$TIMEOUT" \
  #   meshlabserver -i "$input_path_c"/{}/"$MODEL_NAME" -o "$build_path_c"/0_in/{}.off

  python "$MESHFUSION_PATH"/3_meshlabserver.py \
    --in_dir "$input_path_c/*/$MODEL_NAME" \
    --out_dir "$build_path_c"/0_in \
    --out_format off \
    --out_name_pos "$OUT_NAME_POS" \
    --n_proc "$NPROC" \
    --use_pymeshlab

  rm "$build_path_c"/0_in/dummy.png

  echo "Scale meshes"
  python "$MESHFUSION_PATH"/1_scale.py \
    --n_proc "$NPROC" \
    --in_dir "$build_path_c"/0_in \
    --out_dir "$build_path_c"/1_scaled \
    --t_dir "$build_path_c"/1_transform

  echo "Create depths maps"
  python "$MESHFUSION_PATH"/2_fusion.py \
    --mode=render \
    --n_proc "$NPROC" \
    --in_dir "$build_path_c"/1_scaled \
    --out_dir "$build_path_c"/2_depth

  echo "Produce watertight meshes"
  python "$MESHFUSION_PATH"/2_fusion.py \
    --mode=fuse \
    --n_proc "$NPROC" \
    --in_dir "$build_path_c"/2_depth \
    --out_dir "$build_path_c"/2_watertight \
    --t_dir "$build_path_c"/1_transform

  echo "Clean watertight meshes"
  # python "$MESHFUSION_PATH"/clean.py \
  #   --n_proc "$NPROC" \
  #   --in_dir "$build_path_c"/2_watertight \
  #   --out_dir "$build_path_c"/3_watertight_clean

  python "$MESHFUSION_PATH"/3_meshlabserver.py \
    --in_dir "$build_path_c"/2_watertight \
    --out_dir "$build_path_c"/3_watertight_clean \
    --script_path "$MESHFUSION_PATH"/remove.mlx \
    --n_proc "$NPROC" \
    --use_pymeshlab

  echo "Simplify watertight meshes"
  # ls "$build_path_c"/3_watertight_clean | parallel -P "$NPROC" --timeout "$TIMEOUT" \
  #   meshlabserver -i "$build_path_c"/3_watertight_clean/{} -o "$build_path_c"/3_watertight_clean_simple/{} -s "$MESHFUSION_PATH"/simplify.mlx

  python "$MESHFUSION_PATH"/3_meshlabserver.py \
    --in_dir "$build_path_c"/3_watertight_clean \
    --out_dir "$build_path_c"/3_watertight_clean_simple \
    --script_path "$MESHFUSION_PATH"/simplify.mlx \
    --n_proc "$NPROC" \
    --use_pymeshlab

  echo "Process watertight meshes"
  python sample_mesh.py "$build_path_c"/3_watertight_clean_simple \
    --n_proc "$NPROC" \
    --bbox_in_folder "$build_path_c"/0_in \
    --pointcloud_folder "$build_path_c"/4_pointcloud \
    --points_folder "$build_path_c"/4_points \
    --mesh_folder "$build_path_c"/4_mesh \
    --voxels_folder "$build_path_c"/4_voxel \
    --resize \
    --packbits \
    --float16

  echo "Delete temporary files"
  rm -dr "$build_path_c"/0_in \
    "$build_path_c"/1_scaled \
    "$build_path_c"/1_transform \
    "$build_path_c"/2_depth \
    "$build_path_c"/2_watertight \
    "$build_path_c"/3_watertight_clean \
    "$build_path_c"/3_watertight_clean_simple
done

ROOT=..

export MESHFUSION_PATH=$ROOT/external/mesh_fusion
export HDF5_USE_FILE_LOCKING=FALSE # Workaround for NFS mounts

# shellcheck disable=SC2034
INPUT_PATH=$ROOT/data/external/ShapeNetCore.v1
# shellcheck disable=SC2034
CHOY2016_PATH=$ROOT/data/external/Choy2016
# shellcheck disable=SC2034
BUILD_PATH=$ROOT/data/ShapeNet.build
# shellcheck disable=SC2034
OUTPUT_PATH=$ROOT/data/ShapeNet

# shellcheck disable=SC2034
NPROC=16
# shellcheck disable=SC2034
TIMEOUT=180
# shellcheck disable=SC2034
N_VAL=100
# shellcheck disable=SC2034
N_TEST=100
# shellcheck disable=SC2034
N_AUG=50

# shellcheck disable=SC2034
declare -a CLASSES=(
  #  03001627
  #  02958343
  #  04256520
  02691156
  #  03636649
  #  04401088
  #  04530566
  #  03691459
  #  02933112
  #  04379243
  #  03211117
  #  02828884
  #  04090263
  #  02876657 # bottle
  #  02880940  # bowl
  #  02946921  # can
  #  03797390  # mug
)

# Utility functions
lsfilter() {
  folder=$1
  other_folder=$2
  ext=$3

  for f in "$folder"/*; do
    filename=$(basename "$f")
    if [ ! -f "$other_folder/$filename$ext" ] && [ ! -d "$other_folder/$filename$ext" ]; then
      echo "$filename"
    fi
  done
}

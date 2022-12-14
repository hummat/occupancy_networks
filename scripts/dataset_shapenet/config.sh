ROOT=..

export MESHFUSION_PATH="$ROOT/external/mesh_fusion"
export HDF5_USE_FILE_LOCKING=FALSE # Workaround for NFS mounts

SHAPENET_VERSION=v2
INPUT_PATH="$ROOT/data/external/ShapeNetCore.$SHAPENET_VERSION"
CHOY2016_PATH="$ROOT/data/external/Choy2016"
BUILD_PATH="$ROOT/data/ShapeNetCore.$SHAPENET_VERSION.build"
OUTPUT_PATH="$ROOT/data/occ"

NPROC=16
TIMEOUT=180
N_VAL=100
N_TEST=100
N_AUG=50

if [ "$SHAPENET_VERSION" = "v1" ]
then
  MODEL_NAME=model.obj
  OUT_NAME_POS=-2

  declare -a CLASSES=(
    # 02691156 # airplane
    # 02828884 # bench
    # 02876657 # bottle
    02880940 # bowl
    # 02933112 # cabinet
    # 02946921 # can
    # 02958343 # cap
    # 03001627 # chair
    # 03211117 # display
    # 03636649 # lamp
    # 03691459 # speaker
    # 03797390 # mug
    # 04090263 # rifle
    # 04256520 # sofa
    # 04379243 # tool
    # 04401088 # smartphone
    # 04530566 # watercraft
  )
elif [ "$SHAPENET_VERSION" = "v2" ]
then
  MODEL_NAME=models/model_normalized.obj
  OUT_NAME_POS=-3

  declare -a CLASSES=(
    02691156
    02747177 # backpack
    02773838
    02801938
    02808440
    02818832
    02828884
    02843684
    02871439
    02876657
    02880940
    02924116
    02933112
    02942699
    02946921
    02954340
    02958343
    02992529
    03001627
    03046257
    03085013
    03207941
    03211117
    03261776
    03325088
    03337140
    03467517
    03513137
    03593526
    03624134
    03636649
    03642806
    03691459
    03710193
    03759954
    03761084
    03790512
    03797390
    03928116
    03938244
    03948459
    03991062
    04004475
    04074963
    04090263
    04099429
    04225987
    04256520
    04330267
    04379243
    04401088
    04460130
    04468005
    04530566
    04554684
  )
else
  echo "Unknown ShapeNet version $SHAPENET_VERSION"
  exit 1
fi

# Utility functions
lsfilter() {
  folder="$1"
  other_folder="$2"
  ext="$3"

  for f in "$folder"/*
  do
    filename=$(basename "$f")
    if [ ! -f "$other_folder/$filename$ext" ] && [ ! -d "$other_folder/$filename$ext" ]
    then
      echo "$filename"
    fi
  done
}

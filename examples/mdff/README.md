# MDFF Sample

## Data

From [7XCQ](https://www.rcsb.org/3d-view/7XCQ).

- 7xcq.pdb
- 7xcq_validation_2fo-fc_map_coef.cif.gz

## Preprocess

- Create `mrc` file.

```bash
gemmi sf2map 7xcq_validation_2fo-fc_map_coef.cif.gz 7xcq.mrc --mapmask=7xcq.pdb
```

- Crop and add distortion
See `preprocess.ipynb`

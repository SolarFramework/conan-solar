# Open3D Conan recipe for SolAR

Conan 2 recipe building [Open3D](https://www.open3d.org) 0.19.0 from source as a shared library, used by SolARModuleOpen3D
(`open3d/0.19.0@conan-solar/stable`). Linux only; the recipe in `../all` is the Windows one (`open3d/v0.19.0`).

```
recipes/open3D/
├── config.yml
├── all/       open3d/v0.19.0 (Windows)
└── solar/     open3d/0.19.0@conan-solar/stable (Linux, CUDA)
    ├── conanfile.py
    ├── conandata.yml
    ├── create.sh
    ├── patches/0.19.0-0001-glfw-disable-wayland.patch
    └── test_package/
```

## Build

```bash
cd recipes/open3D/solar
./create.sh
```

`create.sh` builds the three published binaries: CUDA Release, CUDA Debug (`cuda_arch` defaults to all-major) and CPU Release.
Remove `-tf ""` to also run `test_package`.
The build needs network access: Open3D downloads its vendored dependencies (and Intel MKL) at configure time.

## Upload

```bash
conan upload "open3d/0.19.0@conan-solar/stable" -r <solar-bump-conan-local remote> --confirm
conan upload "open3d/0.19.0@conan-solar/stable" -r <solar-integration-conan-local remote> --confirm
```

## Use from a SolAR module

`packagedependencies.txt`:

```
open3d|0.19.0|Open3D|conan-solar@conan|conan-solar|shared|with_cuda=True
```

An explicit `cuda_arch` list must use commas: remaken does not quote option values.

## Notes

- `with_gui` is rejected: Open3D's prebuilt Filament requires libc++.
- `fmt` is pinned to the version used by SolARFramework's spdlog; update both together.
- `eigen/3.4.0` is required to keep a single Eigen in the graph.
- `blas=mkl` statically links Intel MKL; `openblas_source` needs gfortran.
- GL and GLFW headers are exposed from `glheaders/` so the vendored Eigen/fmt stay hidden.
- The GLFW patch builds the vendored GLFW for X11 only.
- Debug builds link the vendored TBB as `tbb_debug`.

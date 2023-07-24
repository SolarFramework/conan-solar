# Docker image to build Android dependencies of SolAR

## Description 

This image defines a `build` and a `host` conan profiles and also adds `conan-bcom` and `conan-solar` remotes.

It is based on the android-clang8 image provided by the [ conan-docker-tools](https://github.com/conan-io/conan-docker-tools/tree/master/android-clang_8)

## How to use

### Build image
```
./build.sh
```

### Run container and connect open a Bash session
```
./run.sh
```

### Build dependency

For example you can run `conan install`, but don't forget to specify the `build` and `host` profiles.

```
conan install -pr:b build -pr:h host boost/1.74.0@ -o zlib=False -o bzip2=False -o numa=False -o shared=True -o without_stacktrace=True --build=missing
```

The built binaries will be located by default in your `~/.conan/data` by default, as specified in `run.sh`.

If you want to select another location for the build output, edit `run.sh`. 


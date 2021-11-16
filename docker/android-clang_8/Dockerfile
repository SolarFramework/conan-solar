
FROM conanio/android-clang8

LABEL maintainer="Luis Martinez de Bartolome <luism@jfrog.com>"

ARG CONAN_VERSION

ENV ANDROID_ABI=arm64-v8a \
    CC=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android21-clang \
    CXX=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android21-clang++ \
    LD=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-ld \
    AR=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-ar \
    AS=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-as \
    RANLIB=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-ranlib \
    STRIP=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-strip \
    ADDR2LINE=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-addr2line \
    NM=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-nm \
    OBJCOPY=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-objcopy \
    OBJDUMP=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-objdump \
    READELF=$STANDALONE_TOOLCHAIN/bin/aarch64-linux-android-readelf

RUN pip install conan==1.39.0 \
    && conan profile update settings.arch=armv8 default \
    && conan profile update settings.os=Android default \
    && conan profile update settings.os.api_level=21 default \
    && conan profile update settings.compiler.libcxx=libc++ default

RUN conan profile update settings.compiler.cppstd=17 default

RUN conan remote add conan-solar https://artifact.b-com.com/api/conan/solar-conan-local -i 0

RUN conan remote add conan-bcom https://artifact.b-com.com/api/conan/bcom-conan-local -i 1

RUN conan profile new host \
   && conan profile update settings.arch=armv8 host \
   && conan profile update settings.build_type=Release host \
   && conan profile update settings.compiler=clang host \
   && conan profile update settings.compiler.libcxx=libc++ host \
   && conan profile update settings.compiler.version=8 host \
   && conan profile update settings.os=Android host \
   && conan profile update settings.os.api_level=21 host \
   && conan profile update settings.compiler.cppstd=17 host

RUN conan profile new build \
   && conan profile update settings.arch=x86_64 build \
   && conan profile update settings.build_type=Release build \
   && conan profile update settings.compiler=gcc build \
   && conan profile update settings.compiler.libcxx=libstdc++ build \
   && conan profile update settings.compiler.version=7 build \
   && conan profile update settings.os=Linux build \
   && conan profile update settings.compiler.cppstd=17 build

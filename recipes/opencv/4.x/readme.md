#Opencv recipe

optimization for manage video backend and Dnn
tested with  
- ffmpeg 4.4.4
- gstreamer 1.9.2 and gst-plugin-base 1.9.2
- Intel Openvino 2021.4.1
- Nvidia Cuda 11.5 / Nvidia cudnn 8.3.1.22 

# ffmpeg

Use `conancenter` recipe
or
`conan-solar` recipe with : 

	conan create . 4.4.4@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True 

*Windows issue :*
- with  `libvpx` ?! then add `-o with_libvpx=False` on cmd line. (libvpx seems to be not used on linux). tried with libvpx 1.9.0, 1.10.0, and 1.11.0
- libvpx dependency has been disabled in opencv recipe.

## gstreamer and gst-plugin-base

Gstreamer and Gst-plugin-base recipes have been added.
Currently tested with 1.9.2 version

Use each `conan-solar` recipe with : 
	
	conan create . 1.9.2@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True

## Intel Openvino

[Download](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit-download.html)

[documentation for Windows install](https://docs.openvino.ai/latest/openvino_docs_install_guides_installing_openvino_windows.html)

[documentation for Linux install](https://docs.openvino.ai/latest/openvino_docs_install_guides_installing_openvino_linux.html)

Setup environment variables to detect OpenVino :

- Windows
	
		"C:\Program Files (x86)\IntelSWTools\openvino\bin\setupvars.bat"

- Linux

	By default, the Intel® Distribution of OpenVINO™ is installed to the following directory:

    - For root or administrator: `/opt/intel/openvino_<version>/`

    - For regular users: `/home/<USER>/intel/openvino_<version>/`

	For simplicity, a symbolic link to the latest installation is also created: `/opt/intel/openvino_2021/` or `/home/<USER>/intel/openvino_2021/`

	Please execute (here for regular users) :

		source home/<USER>/intel/openvino_2021/bin/setupvars.sh

	or add to `~/.bashrc`

This script set up environment variables, more particularly INTEL_OPENVINO_DIR.

Opencv recipes check INTEL_OPENVINO_DIR during validation state, and then return an error : "call setupvars.bat/sh script for initialize Intel OpenVino environnement variables"

More details for build Opencv with OpenVino [Here](https://github.com/opencv/opencv/wiki/Intel%27s-Deep-Learning-Inference-Engine-backend)

## NVidia Cudnn

Please follow [cudnn documentation](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)

- CUDA Installation

	Download and install a suitable CUDA version for your system from the NVIDIA website. Best practice would be to follow the installation instructions from the NVIDIA docs.

	The instructions in post are tested with CUDA 10.5, we recommend you the same version.

	download [Cuda toolkits](https://developer.nvidia.com/cuda-toolkit-archive)

- cuDNN Installation

	Download and install a suitable cuDNN version for your system from the NVIDIA website. You can follow the installation instructions from the NVIDIA docs.

	The post has been tested with cuDNN v8.3.1, we recommend you the same version.

	For download Cudnn, you must register to Nvidia Developer Program. 

	download [cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive)
	

Install have been tested with [tar file installation](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html#installlinux-tar) on Linux and with [zip file](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html#installwindows) on Windows

Don't forget to have CUDA_PATH environment variable on Windows!

Information to add cudnn in opencv's conan recipe is from conancenter github : 
	commit be23f3227247549d8792eeff1c7afee7d9abe45a 
	(#8487) opencv/4.5.3: Add support for DNN on CUDA - 07/01/2022	

## Opencv recipe build

- linux

		conan create . 4.5.2@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True -o with_gtk=True -o with_ffmpeg=True -o with_gstreamer=True -o with_openvino=True -o with_cuda=True -o contrib=True -o dnn_cuda=True -o with_cudnn=True -o with_cublas=True

- Windows

		conan create . 4.5.2@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True -o with_ffmpeg=True -o with_gstreamer=True -o with_openvino=True -o with_cuda=True -o contrib=True -o dnn_cuda=True -o with_cudnn=True -o with_cublas=True


explanations :

- 'with_gtk' option doesn't exist on Windows !
- 'contrib' : needed for build
- 'with_ffmpeg' : False by default. For use ffmpeg 4.4.4 (without libvpx on Windows)
- 'with_gstreamer' : False by default. For use gstreamer 1.9.2 (and gst-plugin-base) previously manually created
- 'with_openvino' : False by default. For use Intel OpenVino. defines sub Cmake variables (ENABLE_CXX11=True, and WITH_GRAPH=True) 
- 'with_cuda' : False by default. for use cuda toolkit
- 'dnn_cuda', 'with_cudnn', 'with_cublas' : False by default. For use Cudnn.


### dev informations

for test build with OpenVino and Cudnn with CMake, customize following parameters :  
BUILD_PERF_TESTS:BOOL=OFF 
BUILD_TESTS:BOOL=OFF 
BUILD_DOCS:BOOL=OFF
BUILD_EXAMPLES:BOOL=OFF
WITH_CUDA:BOOL=ON					// Cuda Toolkit 
WITH_INF_ENGINE=ON					// Openvino
ENABLE_CXX11=ON						// Openvino
OPENCV_EXTRA_MODULES_PATH="$myRepo"/opencv_contrib/modules 
CMAKE_INSTALL_PREFIX="$myRepo/install/$RepoSource"
WITH_CUFFT:BOOL=ON					// Cudnn 
WITH_CUDNN:BOOL=ON 					// Cudnn
OPENCV_DNN_CUDA:BOOL=ON				// Cudnn

for add gstreamer in opencv : https://jgsogo.es/conan-community-web/conan-opencv/detail/release-4-1-0_conanfile.html

conan create . opencv/4.5.5@ --build=missing -tf None -o shared=True -o with_ffmpeg=False
conan create . opencv/4.5.5@ --build=missing -tf None -s build_type=Debug -o shared=True -o with_ffmpeg=False
conan create . opencv/4.5.5@ --build=missing -tf None -o shared=True -o with_ffmpeg=False -o contrib=True -o with_cuda=True -o with_cublas=True -o with_cudnn=True -o dnn=True -o dnn_cuda=True -o cuda_arch_bin="75 80 86"
conan create . opencv/4.5.5@ --build=missing -tf None -s build_type=Debug -o shared=True -o with_ffmpeg=False -o contrib=True -o with_cuda=True -o with_cublas=True -o with_cudnn=True -o dnn=True -o dnn_cuda=True -o cuda_arch_bin="75 80 86"
REM conan export . --name=open3d --version=v0.19.0
REM permet de charger la recette en cache local sans la builder, c'est ensuite remaken ou bd/qmake qui la builde)

conan create . --name open3d --version v0.19.0 --build=missing -tf ""
conan create . --name open3d --version v0.19.0  --build=missing -tf "" -s build_type=Debug



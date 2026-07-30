# Recette conan Open3d

package conan pour la recette Open3d

- conanfile - Dep conan.txt 
    recette conan avec des dépendances issues de conan
    a renommer en conanfile.txt pour l'utiliser.

- conanfile.txt : recette avec dependances intégrées (vendored)
    il faut inclure d'autres dépendances dans le projet pour que ce soit fonctionnel :

    open3d|v0.19.0|open3d|conan|conan-center|static
    // pour open3d
    eigen|3.4.0|eigen3|conan|conan-center|static
    // apres changement pour open3d vendored ?!
    fmt|10.2.1|fmt|conan|conan-center|static
    glfw|3.4|glfw3|conan|conan-center|static
    glew|2.2.0|glew|conan|conan-center|static

    et peut etre (ajoutée avant donc pas vu la necessité de l'ajouter après)
    nlohmann_json|3.12.0|nlohmann_json|conan|conan-center|na|


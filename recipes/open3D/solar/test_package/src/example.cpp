// Exercises the Open3D surface actually used by SolARModuleOpen3D: the geometry/Poisson path
// behind SolAROpen3DMeshing, and the legacy Visualizer headers behind SolAROpen3DPointCloudViewer.
#include <cstdio>
#include <memory>
#include <vector>

#include <Eigen/Core>
#include <open3d/Open3D.h>
#include <open3d/visualization/visualizer/Visualizer.h>

int main() {
    // A sphere gives Poisson reconstruction a closed, well-oriented surface to chew on.
    auto sphere = open3d::geometry::TriangleMesh::CreateSphere(1.0, 20);
    auto cloud = sphere->SamplePointsUniformly(5000);

    cloud->EstimateNormals(open3d::geometry::KDTreeSearchParamKNN(30));
    cloud->OrientNormalsConsistentTangentPlane(30);

    auto [mesh, densities] =
            open3d::geometry::TriangleMesh::CreateFromPointCloudPoisson(*cloud, 7);

    std::printf("open3d %s\n", OPEN3D_VERSION);
    std::printf("points   = %zu\n", cloud->points_.size());
    std::printf("vertices = %zu\n", mesh->vertices_.size());
    std::printf("triangles= %zu\n", mesh->triangles_.size());

    if (mesh->triangles_.empty()) {
        std::printf("FAILED: Poisson reconstruction produced no triangles\n");
        return 1;
    }

    // Only construct the Visualizer: creating a window needs a display, which a build agent
    // does not have. This still forces the GL/GLFW headers and symbols to resolve.
    open3d::visualization::Visualizer visualizer;
    (void)visualizer;

    std::printf("OK\n");
    return 0;
}

#include <ifcpp/model/BuildingModel.h>
#include <ifcpp/reader/ReaderSTEP.h>
#include <memory>
#include <iostream>

int main()
{
    // Instanciation du modele IFC
    auto model = std::make_shared<BuildingModel>();
    std::cout << "[OK] IfcPlusPlus 2.5 - BuildingModel instantiated successfully\n";

    // Instanciation du reader STEP
    auto reader = std::make_shared<ReaderSTEP>();
    std::cout << "[OK] IfcPlusPlus 2.5 - ReaderSTEP instantiated successfully\n";

    return 0;
}

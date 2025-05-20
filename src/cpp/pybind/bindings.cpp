#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/numpy.h"

#include "Point.hpp"
#include "PointCloud.hpp"
#include "Material.hpp"
#include "HeatSolver.hpp"
#include "CupGenerator.hpp"

namespace py = pybind11;

PYBIND11_MODULE(heat_transfer, m) {
    m.doc() = "Heat transfer simulation module";
    
    // Enums
    py::enum_<MaterialType>(m, "MaterialType")
        .value("COFFEE", MaterialType::COFFEE)
        .value("CUP_MATERIAL", MaterialType::CUP_MATERIAL) 
        .value("AIR", MaterialType::AIR);
    
    // Position struct
    py::class_<Position>(m, "Position")
        .def(py::init<>())
        .def(py::init<double, double, double>())
        .def_readwrite("x", &Position::x)
        .def_readwrite("y", &Position::y)
        .def_readwrite("z", &Position::z);
    
    // Point class
    py::class_<Point>(m, "Point")
        .def(py::init<double, double, double, double, MaterialType, size_t>())
        .def("get_position", &Point::getPosition)
        .def("get_temperature", &Point::getTemperature)
        .def("set_temperature", &Point::setTemperature)
        .def("get_material", &Point::getMaterial)
        .def("set_material", &Point::setMaterial);
    
    // PointCloud::PointRef class
    py::class_<PointCloud::PointRef>(m, "PointRef")
        .def("get_position", &PointCloud::PointRef::getPosition)
        .def("get_temperature", &PointCloud::PointRef::getTemperature)
        .def("set_temperature", &PointCloud::PointRef::setTemperature)
        .def("get_material", &PointCloud::PointRef::getMaterial)
        .def("get_index", &PointCloud::PointRef::getIndex);
    
    // PointCloud class
    py::class_<PointCloud>(m, "PointCloud")
        .def(py::init<>())
        // For add_point, specify exactly which overload to use
        .def("add_point", static_cast<size_t(PointCloud::*)(double, double, double, double, MaterialType)>(&PointCloud::addPoint))
        // For get_point, we also need to specify exactly which overload
        .def("get_point", static_cast<PointCloud::PointRef(PointCloud::*)(size_t)>(&PointCloud::getPoint), 
             py::return_value_policy::copy)
        .def("size", &PointCloud::size)
        .def("clear", &PointCloud::clear)
        .def("save_to_vtk", &PointCloud::saveToVTK)
        // Add direct access methods in the same class
        .def("get_x", &PointCloud::getX)
        .def("get_y", &PointCloud::getY)
        .def("get_z", &PointCloud::getZ)
        .def("get_temperature", &PointCloud::getTemperature)
        .def("set_temperature", &PointCloud::setTemperature)
        .def("get_material", &PointCloud::getMaterial);
    
    // Material class
    py::class_<Material>(m, "Material")
        .def(py::init<double, double, double, double>())
        .def_static("coffee", &Material::Coffee)
        .def_static("ceramic", &Material::Ceramic)
        .def_static("air", &Material::Air)
        .def("get_density", &Material::getDensity)
        .def("get_specific_heat", &Material::getSpecificHeat)
        .def("get_thermal_conductivity", &Material::getThermalConductivity)
        .def("get_ambient_temperature", &Material::getAmbientTemperature);
    
    // HeatSolver class
    py::class_<HeatSolver>(m, "HeatSolver")
        .def(py::init<PointCloud&, const std::vector<Material>&, double>())
        .def("step", &HeatSolver::step)
        .def("run", &HeatSolver::run_for_time)
        .def("get_current_time", &HeatSolver::getCurrentTime)
        .def("get_average_temperature", &HeatSolver::getAverageTemperature)
        .def("get_max_temperature", &HeatSolver::getMaxTemperature)
        .def("get_min_temperature", &HeatSolver::getMinTemperature);
    
    // CupGenerator class
    py::class_<CupGenerator>(m, "CupGenerator")
        .def(py::init<>())
        .def("generate", &CupGenerator::generate);
    
    // CupGenerator::Parameters class
    py::class_<CupGenerator::Parameters>(m, "CupParameters")
        .def(py::init<>())
        .def_readwrite("inner_radius", &CupGenerator::Parameters::innerRadius)
        .def_readwrite("wall_thickness", &CupGenerator::Parameters::wallThickness)
        .def_readwrite("height", &CupGenerator::Parameters::height)
        .def_readwrite("coffee_height", &CupGenerator::Parameters::coffeeHeight)
        .def_readwrite("point_spacing", &CupGenerator::Parameters::pointSpacing)
        .def_readwrite("coffee_temp", &CupGenerator::Parameters::coffeeTemp)
        .def_readwrite("cup_temp", &CupGenerator::Parameters::cupTemp)
        .def_readwrite("air_temp", &CupGenerator::Parameters::airTemp);
}
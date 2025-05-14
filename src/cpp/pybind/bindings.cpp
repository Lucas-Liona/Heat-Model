#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

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
        .def(py::init<double, double, double, double, MaterialType>())
        .def("get_position", &Point::getPosition)
        .def("get_temperature", &Point::getTemperature)
        .def("set_temperature", &Point::setTemperature)
        .def("get_material", &Point::getMaterial)
        .def("set_material", &Point::setMaterial);
    
    // PointCloud class
    py::class_<PointCloud>(m, "PointCloud")
        .def(py::init<>())
        .def("add_point", &PointCloud::addPoint)
        .def("get_point", static_cast<Point&(PointCloud::*)(size_t)>(&PointCloud::getPoint), 
             py::return_value_policy::reference_internal)
        .def("size", &PointCloud::size)
        .def("clear", &PointCloud::clear)
        .def("save_to_vtk", &PointCloud::saveToVTK);
    
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
        .def("run", &HeatSolver::run)
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
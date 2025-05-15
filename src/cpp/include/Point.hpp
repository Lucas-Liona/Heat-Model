#pragma once

enum class MaterialType {
    COFFEE = 0,
    CUP_MATERIAL = 1,
    AIR = 2
};

struct Position {
    double x, y, z;
    Position() = default;
    Position(double x, double y, double z) : x(x), y(y), z(z) {}
};

class Point {
    /*
    Each point will have a temperature, position, and material. 
    Each point will never move (which is unrealistic) but this means they have the same neighbors for life
    
    To-Do
     (*) Add Neighbors Attribute which is a Vector of (not points but indexes or pointers)
     (*) Get/Set Neighbors (only set Neighbors once)
     (*) Then in solver or in point we need to have max in pool and min in pool for a temperature survey of different neighbors
     (*)
    */
    
public:
    Point(double x, double y, double z, double temp, MaterialType material, size_t index);
    
    Position getPosition() const;
    double getTemperature() const;
    void setTemperature(double temp);
    MaterialType getMaterial() const;
    void setMaterial(MaterialType material);

    size_t index() const;
    std::vector<Point> getNeighbors(); //it might be better to use index's instead
    std::vector<size_t> getNeighborsIndex();
    void setNeighbors(); //append based on index


private:
    Position position_;
    double temperature_;
    MaterialType material_;

    size_t index;
    std::vector<size_t> neighbors_;
};
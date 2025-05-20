# Heat Transfer Simulation

A  heat transfer simulation using C++ with Python visualization to model the way heat dissipates from a coffee cup.

This is 3Blue1Browns playlist on the topic, focusing on Partial Differential Equations to solve the problem

https://youtube.com/playlist?list=PLZHQObOWTQDNPOjrT6KVlfJuKtYTftqH6&si=KGAH1tOJPqrnW8c0

## Features

- Point cloud-based heat transfer simulation
- C++ core for performance with Python bindings
- Interactive 3D visualization
- Real-time dashboard with parameter controls
- Dockerized environment for easy deployment

## Quick Start

### Using Docker (Recommended)

```bash
# clone the repository or open in a codespace and run

docker-compose up --build

```
visit your port 8050 and you should see this

![alt text](image-2.png)

### Here is the radius curve of the coffee cup r given by z
![alt text](image.png)


### To-Do

* The first thing I want to accomplish is changing it from Array of Structures to Structure of Arrays, this will be a significant speed up for 
* Next I will implmenet kd tree for nieghbor finding
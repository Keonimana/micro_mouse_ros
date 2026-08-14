cmake_minimum_required(VERSION 3.8)
project(micro_mouse)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 1. FIND DEPENDENCIES
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(xacro REQUIRED)

# 2. BUILD TARGETS AND XACRO PARSING (If you have C++ nodes later, they go here)
# add_executable(maze_solver src/maze_solver.cpp)
# ament_target_dependencies(maze_solver rclcpp)
set(XACRO_WORLD_INPUT "${CMAKE_CURRENT_SOURCE_DIR}/mouse_sim/worlds/maze_world.sdf.xacro")
set(SDF_WORLD_OUTPUT  "${CMAKE_CURRENT_BINARY_DIR}/worlds/maze_world.sdf")

xacro_add_xacro_file("${XACRO_WORLD_INPUT}" "${SDF_WORLD_OUTPUT}")
add_custom_target(generate_maze_sdf ALL DEPENDS "${SDF_WORLD_OUTPUT}")

# 3. INSTALL MODELS, RULES, AND WORLDS (urdf & launch)
install(
  DIRECTORY
    mouse_sim/urdf
    mouse_sim/launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES
    mouse_sim/worlds/empty_world.sdf
    "${SDF_WORLD_OUTPUT}"
  DESTINATION share/${PROJECT_NAME}/worlds
)

# 4. TESTING
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

# 5. AMENT PACKAGE (MUST ALWAYS BE THE VERY LAST LINE IN THE FILE)
ament_package()

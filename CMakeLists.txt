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

# 2. BATCH PARSE ALL WORLD XACRO FILES
file(GLOB MAZE_XACRO_FILES "${CMAKE_CURRENT_SOURCE_DIR}/mouse_sim/worlds/*.sdf.xacro")

set(ALL_GENERATED_SDFS "")
foreach(XACRO_PATH ${MAZE_XACRO_FILES})
  get_filename_component(FILE_NAME ${XACRO_PATH} NAME_WE)
  
  set(OUTPUT_SDF "${CMAKE_CURRENT_BINARY_DIR}/worlds/${FILE_NAME}.sdf")
  xacro_add_xacro_file("${XACRO_PATH}" "${OUTPUT_SDF}")
  list(APPEND ALL_GENERATED_SDFS "${OUTPUT_SDF}")
endforeach()

add_custom_target(generate_all_sdfs ALL DEPENDS ${ALL_GENERATED_SDFS})

# 3. INSTALLATION OF MODELS AND WORLDS
install(
  DIRECTORY
    config
    launch
    mouse_sim/urdf
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES
    ${ALL_GENERATED_SDFS}
  DESTINATION share/${PROJECT_NAME}/worlds
)
###################################################################
# If non-xacro worlds are going to be included, install them here #
###################################################################

# 4. TESTING
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

# 5. AMENT PACKAGE (MUST ALWAYS BE THE VERY LAST LINE IN THE FILE)
ament_package()

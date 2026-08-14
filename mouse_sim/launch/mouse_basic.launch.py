import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

# Function is called from the command `ros2 launch mouse_basic.launch.py`
def generate_launch_description():

    # Retrieve xacro robot model
    ros_pkg = get_package_share_directory('micro_mouse')
    model_file = os.path.join(
        ros_pkg,
        'urdf',
        'mouse.urdf.xacro'
    )

    robot_description = {
        'robot_description': xacro.process_file(model_file).toxml()
    }

    # Publish transform tree to verify linkages and joints
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description] # Explicitly requires "robot_description"
    )

    # Choose empty Gazebo world for basic launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Spawn the robot into Gazebo (using the robot_description topic)
    spawn_args = [
        '-topic', 'robot_description',
        '-name', 'micro_mouse',
        '-z', '0.01' # Spawn robot above ground to avoid glitches
    ]
    
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=spawn_args,
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_entity
    ])
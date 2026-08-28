import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

# Function is called from the command `ros2 launch mouse.launch.py`
def generate_launch_description():

    # Retrieve launch arguments
    maze_arg = DeclareLaunchArgument(
        'maze_file',
        default_value='maze_world_01.sdf',
        description='Name of the .sdf maze file inside the worlds/ directory'
    )

    # Retrieve xacro robot model, config, and world files
    ros_pkg = get_package_share_directory('micro_mouse')
    model_path = os.path.join(ros_pkg, 'urdf', 'mouse.urdf.xacro')
    config_path = os.path.join(ros_pkg, 'config', 'slam_params.yaml')
    worlds_dir = os.path.join(ros_pkg, 'worlds')
    gz_path = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')

    # Retrieve correct maze file argument
    world_path = PathJoinSubstitution([
        worlds_dir,
        LaunchConfiguration('maze_file')
    ])

    robot_description = {
        'robot_description': xacro.process_file(model_path).toxml()
    }

    gazebo_worlds = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[f"{worlds_dir}:{gz_path}" if gz_path else worlds_dir]
    )

    # Publish transform tree to verify linkages and joints
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description] # Explicitly requires "robot_description"
    )

    # Utilize Gazebo Environmet for Mapping + Localization
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            config_path,
            {'use_sim_time': True}
        ]
    )

    # Gazebo Sim Launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ]),
        launch_arguments={'gz_args': ['-r ', world_path]}.items()
    )

    # Spawn the robot into Gazebo (using the robot_description topic)
    spawn_args = [
        '-topic', 'robot_description',
        '-name', 'micro_mouse',
        '-x', str(0.18 * 8 - 0.09),
        '-y', str(-0.18 * 8 + 0.09),
        '-z', '0.01',
        '-Y', '3.14'

    ]
    
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=spawn_args,
        output='screen'
    )

    # Messaging bridge between ROS and Gazebo
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan'
        ],
        output='screen'
    )

    return LaunchDescription([
        maze_arg,
        gazebo_worlds,
        robot_state_publisher,
        slam_node,
        gazebo,
        spawn_entity,
        ros_gz_bridge
    ])
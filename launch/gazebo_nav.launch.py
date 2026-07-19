from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_path = get_package_share_directory('tarobot_one')
    
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            pkg_path, 'launch', 'gazebo.launch.py')])
    )

    slam_params = os.path.join(pkg_path, 'config', 'mapper_params_online_async.yaml')

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')]),
        launch_arguments={
            'slam_params_file': slam_params,
            'use_sim_time': 'true'
        }.items()
    )

    nav2_params = os.path.join(pkg_path, 'config', 'nav2_params.yaml')

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')]),
        launch_arguments={
            'params_file': nav2_params,
            'use_sim_time': 'true'
        }.items()
    )
    
    rviz_config = os.path.join(pkg_path, 'rviz', 'real_navigation.rviz')
    rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz'
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=None,   # can be changed IfCondition(LaunchConfiguration('use_rviz'))
        output='screen'
    )
                        
    return LaunchDescription([
        gazebo_sim,
        slam_toolbox,
        nav2_bringup,
        rviz_arg,
        rviz_node
    ])
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
import os
from ament_index_python.packages import get_package_share_path

def generate_launch_description():

    rviz_config_path = os.path.join(get_package_share_path('tarobot_one'),
                             'rviz', 'nav2_sim.rviz')
    
    world = os.path.join(get_package_share_path('tarobot_one'),'worlds','indoor_sim.world')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_path('tarobot_one'),'launch','rsp.launch.py')]),
                launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'false'}.items()
        )

    gazebo_world = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
            get_package_share_path('ros_gz_sim'), 'launch', 'gazebo.launch.py')]),
            launch_arguments = {'world' : world}.items()
            )
    
    spawn_entity = Node(package='ros_gz_sim', executable='spawn_entity.py',
                arguments=['-topic', 'robot_description',
                            '-entity', 'robot'],
                output='screen')

    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=['-d', rviz_config_path]
    )
                        
    return LaunchDescription([
        rsp,
        gazebo_world,
        spawn_entity,
        rviz2_node
    ])
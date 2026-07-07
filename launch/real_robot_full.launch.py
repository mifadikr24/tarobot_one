# All-in-one launch for REAL ROBOT deployment.
# Untuk: Raspberry Pi 4 + LD19 LiDAR + 4WD diff-drive
#
# Author: Mifad Ikromullah
# Created: 2026-05-02 
# That is launched:
#   1. robot_state_publisher (via rsp.launch.py)
#   2. twist_mux
#   3. controller_manager + diff_cont + joint_broad
#   4. LD19 LiDAR (via lidar_ld19.launch.py)
#   5. SLAM Toolbox (mapping mode)
#   6. Nav2 stack
#
# Usage:
#   ros2 launch tarobot_one real_robot_full.launch.py
#
# Optional args:
#   slam:=true|false   (default: true)
#   nav2:=true|false   (default: true)
#   lidar:=true|false  (default: true)

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    DeclareLaunchArgument,
    RegisterEventHandler,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch.event_handlers import OnProcessStart
from launch.conditions import IfCondition

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_name = 'tarobot_one'
    pkg_share = get_package_share_directory(package_name)

    # ─── Launch arguments ───────────────────────────────────
    slam_arg = DeclareLaunchArgument(
        'slam', default_value='true',
        description='Run SLAM Toolbox in mapping mode')

    nav2_arg = DeclareLaunchArgument(
        'nav2', default_value='true',
        description='Run Nav2 stack')

    lidar_arg = DeclareLaunchArgument(
        'lidar', default_value='true',
        description='Run LiDAR driver')

    use_slam = LaunchConfiguration('slam')
    use_nav2 = LaunchConfiguration('nav2')
    use_lidar = LaunchConfiguration('lidar')

    # ─── Param files ────────────────────────────────────────
    slam_params_file = os.path.join(
        pkg_share, 'config', 'mapper_params_real_robot.yaml')

    nav2_params_file = os.path.join(
        pkg_share, 'config', 'nav2_params_real_robot.yaml')

    twist_mux_params = os.path.join(
        pkg_share, 'config', 'twist_mux.yaml')

    controller_params_file = os.path.join(
        pkg_share, 'config', '4wheel_controllers.yaml')

    # URDF processed by xacro
    xacro_file = os.path.join(
        pkg_share, 'description', 'urdf', 'robot.urdf.xacro')

    # ─── 1. Robot State Publisher (include rsp.launch.py) ───
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            pkg_share, 'launch', 'rsp.launch.py')]),
        launch_arguments={
            'use_sim_time': 'false',
            'use_ros2_control': 'true'
        }.items()
    )

    # ─── 2. Twist Mux ───────────────────────────────────────
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_mux_params, {'use_sim_time': False}],
        remappings=[('/cmd_vel_out', '/diff_cont/cmd_vel_unstamped')]
    )

    # ─── 3. Controller Manager ──────────────────────────────
    # FIX: Wrap robot_description with ParameterValue to ensure string parsing
    robot_description_param = ParameterValue(
        Command([
            'xacro ', xacro_file,
            ' use_ros2_control:=true',
            ' sim_mode:=false'
        ]),
        value_type=str
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description_param},
            controller_params_file
        ]
    )

    delayed_controller_manager = TimerAction(
        period=3.0, actions=[controller_manager])

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont']
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad']
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    # ─── 4. LD19 LiDAR ──────────────────────────────────────
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            pkg_share, 'launch', 'lidar_ld19.launch.py')]),
        condition=IfCondition(use_lidar)
    )

    # ─── 5. SLAM Toolbox (delayed 5s) ───────────────────────
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        # [FIX] output: 'screen' → 'log'
        # The warning "LaserRangeScan contains X readings, expected Y" is an old bug
        # in slam_toolbox (github.com/SteveMacenski/slam_toolbox/issues/278)
        # that prints directly to stdout, not the ROS logger, so it cannot be
        # disabled from mapper_params.yaml or any parameter.
        # With 'log', stdout is redirected to ~/.ros/log/ — a clean terminal,
        # SLAM continues to run normally, warnings can still be seen in the log file.
        output='log',
        parameters=[
            slam_params_file,
            {'use_sim_time': False}
        ],
        condition=IfCondition(use_slam)
    )

    delayed_slam = TimerAction(period=8.0, actions=[slam_node])

    # ─── 6. Nav2 (delayed 8s) ───────────────────────────────
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch', 'navigation_launch.py')
        ]),
        launch_arguments={
            'use_sim_time': 'false',
            'params_file': nav2_params_file,
            'autostart': 'true',
        }.items(),
        condition=IfCondition(use_nav2)
    )

    delayed_nav2 = TimerAction(period=12.0, actions=[nav2_launch])

    # ─── Assemble ────────────────────────────────────────────
    return LaunchDescription([
        slam_arg,
        nav2_arg,
        lidar_arg,
        rsp,
        twist_mux,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
        lidar_launch,
        delayed_slam,
        delayed_nav2,
    ])
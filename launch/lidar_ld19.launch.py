import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        DeclareLaunchArgument(
            name='topic_name', 
            default_value='scan',
            description='Laser Topic Name'
        ),

        DeclareLaunchArgument(
            name='frame_id', 
            default_value='lidar_link',
            description='Laser Frame ID'
        ),

        DeclareLaunchArgument(
            name='lidar_transport',
            default_value='serial',
            description='Lidar transport: serial, udp_server, udp_client, tcp_server, tcp_client'
        ),

        DeclareLaunchArgument(
            name='lidar_serial_port',
            default_value='/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.1:1.0-port0',
            description='Lidar serial port device name'
        ),

        DeclareLaunchArgument(
            name='lidar_server_ip',
            default_value='0.0.0.0',
            description='Lidar server ip'
        ),

        DeclareLaunchArgument(
            name='lidar_server_port',
            default_value='8889',
            description='Lidar server port number'
        ),

        Node(
            package='ldlidar_stl_ros2',
            executable='ldlidar_stl_ros2_node',
            name='ld19',
            output='screen',
            parameters=[
                {'product_name': 'LDLiDAR_LD19'},
                {'topic_name': LaunchConfiguration('topic_name')},
                {'frame_id': LaunchConfiguration('frame_id')},
                {'comm_mode': LaunchConfiguration('lidar_transport')},
                {'port_name': LaunchConfiguration('lidar_serial_port')},
                {'port_baudrate': 230400},
                {'server_ip': LaunchConfiguration('lidar_server_ip')},
                {'server_port': LaunchConfiguration('lidar_server_port')},
                {'laser_scan_dir': True},
                # {'bins': 0},
                {'enable_angle_crop_func': False},
                {'angle_crop_min': 150.0},
                {'angle_crop_max': 210.0}
            ]
        )
    ])
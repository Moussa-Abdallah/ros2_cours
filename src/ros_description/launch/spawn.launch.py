import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('ros_description')

    xacro_file      = os.path.join(pkg_share, 'urdf', 'diff_drive_bot.urdf.xacro')
    controllers_cfg = os.path.join(pkg_share, 'config', 'controllers.yaml')
    rviz_cfg        = os.path.join(pkg_share, 'rviz', 'display.rviz')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Utiliser /clock de Gazebo'
    )
    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Lancer RViz'
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': '-r -v 4 empty.sdf'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time':     LaunchConfiguration('use_sim_time'),
        }],
    )

    # On publie d'abord le robot sur /robot_description (robot_state_publisher),
    # puis on demande à Gazebo de créer l'entité depuis ce topic.
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name',  'diff_drive_bot',
            '-z',     '0.1',
        ],
        output='screen',
    )
        # ---------- Pont Gazebo → ROS pour /clock ----------
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    # gz_ros2_control démarre déjà un controller_manager.
    # On n'a donc PAS besoin de lancer controller_manager.
    # On lance juste les "spawners" qui chargent/démarrent les contrôleurs.
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    diff_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    # Le 1er contrôleur doit attendre la fin du spawn.
    delay_jsb = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster],
        )
    )
    # Le diff_drive_controller attend le joint_state_broadcaster.
    delay_ddc = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster,
            on_exit=[diff_drive_controller],
        )
    )

    return LaunchDescription([
        use_sim_time_arg,
        rviz_arg,
        gazebo,
        clock_bridge,
        robot_state_publisher,
        spawn_entity,
        delay_jsb,
        delay_ddc,
        rviz,
    ])
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_share = get_package_share_directory('ros_description')

    default_model_path = os.path.join(
        pkg_share, 'urdf', 'diff_drive_bot.urdf.xacro'
    )
    default_rviz_config = os.path.join(
        pkg_share, 'rviz', 'display.rviz'
    )

    model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model_path,
        description='Chemin absolu vers le fichier URDF ou Xacro'
    )
    rviz_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=default_rviz_config,
        description='Chemin absolu vers la config RViz'
    )
    use_gui_arg = DeclareLaunchArgument(
        name='use_joint_state_publisher_gui',
        default_value='true',
        description='Lancer joint_state_publisher_gui (sliders)'
    )
    use_sim_time_arg = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='false',
        description='Utiliser /clock (simulation)'
    )

    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_joint_state_publisher_gui'))
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        condition=UnlessCondition(LaunchConfiguration('use_joint_state_publisher_gui'))
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    return LaunchDescription([
        model_arg,
        rviz_arg,
        use_gui_arg,
        use_sim_time_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        joint_state_publisher,
        rviz,
    ])
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    ExecuteProcess,
    DeclareLaunchArgument,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_bot'

    # 默认 world 文件路径
    default_world = os.path.join(
        get_package_share_directory(package_name),
        'worlds', 'obstacles.world'
    )

    # 声明 world 参数（命令行可覆盖）
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Path to the Gazebo world file'
    )

    world_file = LaunchConfiguration('world')

    # 1. robot_state_publisher（开启仿真时间）
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. 只启动 gzserver，不启动 gzclient（避免抢资源导致崩溃），加载指定 world
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]),
        launch_arguments={
            'world': world_file,
            'gui': 'false'
        }.items()
    )

    # 3. 把 URDF 生成到 Gazebo 里
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'my_bot'],
        output='screen'
    )

    # 4. 延迟 5 秒再启动 gzclient，等 gzserver 完全就绪
    gazebo_client = TimerAction(
        period=5.0,
        actions=[
            ExecuteProcess(
                cmd=['gzclient'],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        world_arg,
        rsp,
        gazebo_server,
        spawn_entity,
        gazebo_client,
    ])
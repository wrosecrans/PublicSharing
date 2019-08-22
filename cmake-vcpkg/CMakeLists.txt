cmake_minimum_required(VERSION 3.15)


add_subdirectory("liba")
add_subdirectory("libb")


project("SuperApp")

find_package(Qt5 COMPONENTS Core Gui Widgets Multimedia OpenGL Qml WebEngineWidgets REQUIRED)



# Install script for directory: /home/andregomes/FS-MACplus/gr-fsmac/include/fsmac

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/fsmac" TYPE FILE FILES
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/api.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/csma.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/tdma.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/sens_num_senders.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/exchanger.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/latency_sensor.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/metrics_sensor.h"
    "/home/andregomes/FS-MACplus/gr-fsmac/include/fsmac/snr.h"
    )
endif()


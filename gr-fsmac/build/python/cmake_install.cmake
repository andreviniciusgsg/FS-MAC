# Install script for directory: /home/gnuradio/FS-MACplus/gr-fsmac/python

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python2.7/dist-packages/fsmac" TYPE FILE FILES
    "/home/gnuradio/FS-MACplus/gr-fsmac/python/__init__.py"
    "/home/gnuradio/FS-MACplus/gr-fsmac/python/decision.py"
    "/home/gnuradio/FS-MACplus/gr-fsmac/python/ml_decision.py"
    )
endif()

if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Unspecified")
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python2.7/dist-packages/fsmac" TYPE FILE FILES
    "/home/gnuradio/FS-MACplus/gr-fsmac/build/python/__init__.pyc"
    "/home/gnuradio/FS-MACplus/gr-fsmac/build/python/decision.pyc"
    "/home/gnuradio/FS-MACplus/gr-fsmac/build/python/ml_decision.pyc"
    "/home/gnuradio/FS-MACplus/gr-fsmac/build/python/__init__.pyo"
    "/home/gnuradio/FS-MACplus/gr-fsmac/build/python/decision.pyo"
    "/home/gnuradio/FS-MACplus/gr-fsmac/build/python/ml_decision.pyo"
    )
endif()


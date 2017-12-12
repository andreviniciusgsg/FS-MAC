#!/bin/bash
echo
echo "====== INSTALLING swig ======"
sudo apt-get install swig
echo

echo
echo "====== INSTALLING liblog4cpp5 ======"
sudo apt-get install liblog4cpp5-dev
echo 

echo
echo "====== INSTALLING python-matplotlib ======"
sudo apt-get install python-matplotlib
echo

echo
echo "====== INSTALLING libboost-all-dev ======"
sudo apt-get install libboost-all-dev
echo

echo
echo "====== INSTALLING gr-foo ======"
echo

cd ~/
git clone -b master https://github.com/bastibl/gr-foo
cd gr-foo
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig

echo
echo "====== INSTALLING gr-eventstream ======"
echo

cd ~/
git clone https://github.com/osh/gr-eventstream
cd gr-eventstream
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig

echo
echo "====== INSTALLING gr-uhdgps ======"
echo

cd ~/
git clone https://github.com/osh/gr-uhdgps
cd gr-uhdgps
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig

echo
echo "====== INSTALLING gr-ieee802-15-4 ======"
echo

cd ~/
git clone -b master https://github.com/bastibl/gr-ieee802-15-4
cd gr-ieee802-15-4
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
cd ../examples
grcc ieee802_15_4_OQPSK_PHY.grc

echo "====== Pip ======"
sudo apt install python-pip

echo "====== Scikit-Learn ======"
echo
sudo pip install -U scikit-learn 

echo
echo "====== INSTALLING FS-MAC ======"
echo

cd ~/
if [[ ! -e FS-MACplus ]]; then
	git clone https://github.com/andreviniciusgsg/FS-MACplus.git
fi
cd FS-MACplus
cd gr-fsmac
if [[ -e build ]]; then
	sudo rm -rf build;
fi
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig



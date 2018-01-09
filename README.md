# Introduction
This project is an extension of FS-MAC. You can find more information [here](https://github.com/jeffRayneres/FS-MAC). FS-MAC+ provides a flexible and smart MAC sublayer. It implements machine learning techniques in order to select the best MAC protocol over time. All the implementation is done in Gnu Radio ([see more details](http://gnuradio.org/)) and using USRP Software Defined Radios ([see more details](https://www.ettus.com/)).

# MAC protocols
FS-MAC+ currently has 2 MAC protocols available, CSMA/CA and TDMA.

# PHY
The physical layer is based on the standard IEEE 802.15.4. This project is called IEEE 802.15.4 ZigBee Transceiver. You can find more information on this [link](https://github.com/bastibl/gr-ieee802-15-4). Please refer to that.

# Dependencies
FS-MAC+ depends on dependencies from both FS-MAC and IEEE 802.15.4 ZigBee Transceiver. Furthermore, FS-MAC+ also depends on `octave`, `oct2py` and `scikit-learn` for machine learning purposes. An installation script is provided with all requirements.

# Installation
In order to make life easier, an installation script is provided. It is called `install.sh`. All dependencies are installed by this script. It also installs FS-MAC+. By default, source code and dependencies are downloaded in the `home` directory. If nothing is changed, you should find the FS-MAC+ code on `~/FS-MACplus/gr-fsmac`.

Attention! `install.sh`assumes you already have Gnu Radio installed on you computer. If it is not the case, install Gnu Radio before executing `install.sh`. You can find more information about Gnu Radio installation on this [link](https://wiki.gnuradio.org/index.php/InstallingGR). If you opt to install Gnu Radio from github repository, make sure you select the master branch. It is important for compatibilities issues with other tools on `install.sh`. `install.sh` also assumes Ubuntu as the host O.S. I have tested it on Ubuntu 16.04 but I am quite confident you would have no problem using any 16.04+. Please, report any errors.

# Examples
You can find some examples on folder gr-fsmac/examples. There are ready-to-go transceivers available. So, feel free to run some examples before to explore the project.

# Contact
You are free to reach me if you wish to. My email is andre.gomes@dcc.ufmg.br. You can also find more information on [https://homepages.dcc.ufmg.br/~andre.gomes](https://homepages.dcc.ufmg.br/~andre.gomes).

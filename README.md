
# Attention!
Be carefull! It's still a work in progress. You may find it difficult to use right now and probably several problems. It will get better as soon as the project ends or reach a senior stage.

# Introduction
This project is an extension of FS-MAC. You can find more information [here](https://github.com/jeffRayneres/FS-MAC). FS-MAC+ provides a flexible and smart MAC sublayer. It implements machine learning techniques in order to select the best MAC protocol over time.

# MAC protocols
FS-MAC+ currently has 2 MAC protocols available, CSMA/CA and TDMA.

# PHY
The physical layer is based on the standard IEEE 802.15.4. This project is called IEEE 802.15.4 ZigBee Transceiver. You can find more information on this [link](https://github.com/bastibl/gr-ieee802-15-4). Please refer to that.

# Dependencis
FS-MAC+ depends on dependencies from both FS-MAC and IEEE 802.15.4 ZigBee Transceiver. Furthermore, FS-MAC+ also depends on `octave` for machine learning purposes. An installation script is provided with all requirements.

# Installation
In order to make life easier, an installation script is provided. It is called `install.sh`. All dependencies are installed by this script. It also installs FS-MAC+. By default, source code and dependencies are downloaded in the `home` directory. If nothing is changed, you should find the FS-MAC+ code on `~/FS-MACplus/gr-fsmac`.

# Examples
You can find some examples on folder gr-fsmac/examples. There are ready-to-go transceivers available. So, feel free to run some examples before to explore the project.

# Contact
You are free to reach me if you wish to. My email is andre.gomes@dcc.ufmg.br. You can also find more information on [https://homepages.dcc.ufmg.br/~andre.gomes](https://homepages.dcc.ufmg.br/~andre.gomes).
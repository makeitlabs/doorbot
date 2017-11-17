Configuring a PathPilot install to run PyQt4


====
point to old ubuntu release repos, adapted from:
https://smyl.es/how-to-fix-ubuntudebian-apt-get-404-not-found-package-repository-errors-saucy-raring-quantal-oneiric-natty/

sudo sed -i -e 's/archive.ubuntu.com\|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
sudo sed -i -e 's/us.old-releases.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
sudo apt-get update
====

Install git:
sudo apt-get install git-core



Set up PyQt4 for Python3, adapted from:
http://stackoverflow.com/questions/7942887/how-to-configure-pyqt4-for-python-3-in-ubuntu


sudo apt-get install build-essential python3-dev libqt4-dev python3-setuptools


build sip-4.18.1:
python3 configure.py
make
sudo make install



build PyQt-x11-gpl-4.11.4:
python3 configure.py
make
sudo make install



build enum34-1.1.6:
python3 setup.py build
sudo python3 setup.py install


build pyserial-3.2.1:
python3 setup.py build
sudo python3 setup.py install

build six-1.11.0:
python3 setup.py build
sudo python3 setup.py install

build python-dateutil-2.6.0:
python3 setup.py build
sudo python3 setup.py install

install Qt4 designer:
sudo apt-get install qt4-designer

install PyQt tools
sudo apt-get install pyqt-tools


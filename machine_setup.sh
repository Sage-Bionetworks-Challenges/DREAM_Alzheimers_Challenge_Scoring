sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y emacs
sudo apt-get install -y r-base
sudo apt-get install -y r-base-dev

sudo apt-get install -y python-dev
sudo apt-get install -y python-pip

sudo pip install rpy2
sudo pip install synapseclient

sudo Rscript -e 'options(repos="http://cran.fhcrc.org/"); install.packages("pROC")'


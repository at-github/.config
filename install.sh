# ZSH
if [ ! -d $HOME/.oh-my-zsh ]; then
  echo "Clone oh my zsh";
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
  rm -rf $HOME/.oh-my-zsh
  git submodule init
  git submodule update
fi

if [ ! -f $HOME/.zshenv ]; then
  ln -s $HOME/.config/zsh/.zshenv $HOME/.zshenv
fi

if [ ! -d $HOME/.oh-my-zsh ]; then
  echo "Clone oh my zsh";
  git clone https://github.com/olivierverdier/zsh-git-prompt.git
fi

if ! [ -x "$(command -v python)" ]; then
  echo "Install python for almost the prompt"
  sudo apt install python-is-python3
fi

if [ ! -d $HOME/.config/zsh/.oh-my-zsh/custom/plugins/zsh-autosuggestions ]; then
  echo "clone zsh-autosuggestions";
  git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
fi

if [ ! -d $HOME/.config/zsh/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting ]; then
  echo "clone zsh-syntax-highlighting";
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
fi

# Zoxide
# curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash

# Neovim
# Neovim > 0.7
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:neovim-ppa/stable
sudo apt-get update
sudo apt-get install neovim

git clone --depth 1 https://github.com/wbthomason/packer.nvim\
 ~/.local/share/nvim/site/pack/packer/start/packer.nvim

sudo apt install ripgrep fd-find python3-pip python3-neovim npm

pip3 install pynvim

sudo npm install -g neovim eslint

php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
php -r "if (hash_file('sha384', 'composer-setup.php') === '55ce33d7678c5a611085589f1f3ddf8b3c52d662cd01d4ba75c0ee0459970c2200a51f492d557530c71c15d8dba01eae') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
php composer-setup.php
php -r "unlink('composer-setup.php');"

# TODO prompt telling to install node

sudo mv composer.phar /usr/local/bin/composer
composer global require "squizlabs/php_codesniffer=*"

nvim +PackerSync
nvim +PackerCompile

# ZSH
if [ ! -d $HOME/.oh-my-zsh ]; then
  echo "Clone oh my zsh";
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

if [ ! -f $HOME/.config/zsh/.zshenv ]; then
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

# ZSH
# TODO check oh-my-zsh is installed
if [ ! -d $HOME/.oh-my-zsh ]; then
  echo "Clone oh my zsh";
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

if [ ! -f $HOME/.config/zsh/.zshenv ]; then
  ln -s $HOME/.config/zsh/.zshenv $HOME/.zshenv
fi

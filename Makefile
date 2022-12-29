.PHONY: check-and-reinit-submodules zsh docker-build docker-build-without-cache docker-jump help composer

help:
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][[:alnum:]_-]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t

# Get submodules
get-submodules:
	@if git submodule status | egrep -q '^[-]|^[+]' ; then \
		echo "INFO: Need to reinitialize git submodules"; \
		git submodule update --init; \
	fi

# Install php composer
composer:
	DEBIAN_FRONTEND=noninteractive apt install php-cli composer -y

# Install zsh dependencies
zsh: get-submodules
	apt update
	apt install python-is-python3 -y
	ln -s ~/.config/zsh/.zshenv ~/.zshenv;
	git clone https://github.com/zsh-users/zsh-autosuggestions \
		~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-autosuggestions
	git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
		~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
	curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh \
		| bash
	zsh

# Install neovim
neovim: get-submodules composer
	# To get started, first clone this repository to somewhere on your packpath, e.g.:
	git clone --depth 1 https://github.com/wbthomason/packer.nvim\
		~/.local/share/nvim/site/pack/packer/start/packer.nvim
	apt install \
		cargo \
		eslint \
		fd-find \
		gcc \
		gem \
		luarocks \
		npm \
		python3-neovim \
		python3-pip \
		ripgrep \
		ruby \
		ruby-dev \
		wget \
		-y
	pip3 install pynvim
	gem install neovim
	npm install -g tree-sitter-cli neovim 
	apt-get install neovim -y
	nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'

# Build image
docker-build:
	docker build -t tarik/forconfig:alpha .

# Build image without cache (force download)
docker-build-without-cache:
	docker build -t tarik/forconfig:alpha --no-cache .

# Jump into the container
docker-jump:
	# --network="host" help PackerUpdate to download easily
	docker run -it --network="host" tarik/forconfig:alpha

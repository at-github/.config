MAKEFLAGS += --silent

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
	([ ! -f ~/.zshenv ]) && ln -s ~/.config/zsh/.zshenv ~/.zshenv || echo 'Alias already exist'
	([ ! -d ~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-autosuggestions ]) && git clone https://github.com/zsh-users/zsh-autosuggestions \
		~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-autosuggestions || echo 'zsh-autosuggestions already installed'
	([ ! -d ~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting ]) && git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
		~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting || echo 'zsh-syntax-highlighting already installed'
	(! type zoxide > /dev/null) && curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh \
		| bash || echo 'Zoxide already installed'
	zsh

# Install neovim
neovim: get-submodules composer
	# To get started, first clone this repository to somewhere on your packpath, e.g.:
	git clone --depth 1 https://github.com/wbthomason/packer.nvim\
		~/.local/share/nvim/site/pack/packer/start/packer.nvim
	apt install \
		fd-find \
		gem \
		npm \
		python3-neovim \
		python3-pip \
		ruby \
		ruby-dev \
		-y
	pip3 install pynvim
	npm install -g tree-sitter-cli neovim 

	apt-get install ninja-build \
   		gettext libtool libtool-bin \
   		autoconf automake cmake g++ \
   		pkg-config unzip -y
	mkdir -p ~/.local/bin/nvim
	git clone https://github.com/neovim/neovim.git
	cd neovim && git checkout tags/v0.8.3 -b v0.8.3 && make CMAKE_BUILD_TYPE=Release \
		CMAKE_INSTALL_PREFIX=~/.local/bin/nvim install

	~/.local/bin/nvim/bin/nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'

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

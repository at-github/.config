.PHONY: check-and-reinit-submodules zsh docker-build docker-build-without-cache docker-jump help

help:
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][[:alnum:]_-]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t

# Get submodules
get-submodules:
	@if git submodule status | egrep -q '^[-]|^[+]' ; then \
		echo "INFO: Need to reinitialize git submodules"; \
		git submodule update --init; \
	fi

# Install zsh dependancies
zsh: get-submodules
	apt install python-is-python3 -y
	ln -s ~/.config/zsh/.zshenv ~/.zshenv;
	git clone https://github.com/zsh-users/zsh-autosuggestions ~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-autosuggestions
	git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
	curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash
	zsh

# Build image
docker-build:
	docker build -t tarik/forconfig:alpha .

# Build image without cache (force download)
docker-build-without-cache:
	docker build -t tarik/forconfig:alpha --no-cache .

# Jump into the container
docker-jump:
	docker run -it tarik/forconfig:alpha

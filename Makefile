.PHONY: check-and-reinit-submodules zsh docker-build docker-build-without-cache docker-jump

check-and-reinit-submodules:
	@if git submodule status | egrep -q '^[-]|^[+]' ; then \
		echo "INFO: Need to reinitialize git submodules"; \
		git submodule update --init; \
	fi

zsh:
	apt install python-is-python3 -y
	ln -s ~/.config/zsh/.zshenv ~/.zshenv;
	git clone https://github.com/zsh-users/zsh-autosuggestions ~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-autosuggestions
	git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.config/zsh/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
	curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash
	source ~/.zshenv

docker-build:
	docker build -t tarik/forconfig:alpha .

docker-build-without-cache:
	docker build -t tarik/forconfig:alpha --no-cache .

docker-jump:
	docker run -it tarik/forconfig:alpha

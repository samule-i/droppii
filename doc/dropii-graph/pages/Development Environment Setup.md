- #+BEGIN_WARNING
  Development documentation is currently only available under linux / mac operating systems, if you are using Windows it is recommended you use [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
  #+END_WARNING
- ```sh
  git clone https://github.com/samule-i/droppii.git
  make dev-init
  ```
-
- dev-init will
	- Install a local python 3.11 binary if python 3.11 is not detected
	- Setup a virtual environment
	- Install developer dependencies
	- Install project dependencies
	- Install the droppii package in editable mode
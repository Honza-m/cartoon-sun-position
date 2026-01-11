# Sun position image

Generates an image of the sun's position in the sky for the current time. Uses home assistant to get the current sun position to getnerate the image file.

## Configuration
Before running, the Home Assistant API credentials need to be configured to retrieve the position of the sun for today.
See .env.example for reference. The credentials are collected either from a .env file or directly from the environment.

## Installation
On Raspberry Pi Zero, I also had to install the following for uv to be able to compile the Pillow library from source.
    ```bash
    sudo apt install -y zlib1g-dev libjpeg-dev python3-dev libfreetype6-dev
    ```
### As a dependency
The package isn't published anywhere, but you can install it as a local dependency.
1. Clone the repository
2. Activate the virtual environment of the project you want to use this in
3. `pip install -e /path/to/the/cloned/repository`

### As a standalone tool
1. Clone the repository
2. Install the package:
    ```bash
    uv sync
    ```
3. Run `uv run generate` to generate the image. The image will be generated in ./output


## TODO
- Cache homeassistant config
- Generate a sun position/palette file together with the image to check if image has/needs to change

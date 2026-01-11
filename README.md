# Sun position image

Generates an image of the sun's position in the sky for the current time. Uses home assistant to get the current sun position to getnerate the image file.

## Installation
1. Clone the repository
2. On Raspberry Pi Zero, I also had to install the following for uv to be able to compile the Pillow library from source.
    ```bash
    sudo apt install -y zlib1g-dev libjpeg-dev python3-dev libfreetype6-dev
    ```
3. Install the required Python dependencies:
    ```bash
    uv sync
    ```
4. Create an .env file with your Home Assistant details. See .env.example for reference.
5. `uv run python main.py`. Image for the current will be generated in ./output/.

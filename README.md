# Sims Linux Bottle Installer

Installs The Sims 1 into a Bottle (Windows app container) on a Linux host.

This script specifically targets
[The Sims - Complete Collection](https://www.simsnetwork.com/simpedia/the-sims/editions/the-sims-complete-collection)
but may work with other releases.

## Usage

### Create Game Data Zip

1. Install 'The Sims - Complete Collection' to a PC, Windows VM, temporary Bottle, etc.
2. Browse to the game installation location, this defaults to ` C:\Program Files (x86)\Maxis\The Sims`
3. Browse up one level so that you can see the `The Sims` game folder
4. Compress the `The Sims` game folder into a zip file
5. Move your zip file somewhere easy to find, such as your Downloads folder: `~/Downloads/sims.zip`

### Running the Installer

1. Install [Bottles](https://flathub.org/apps/com.usebottles.bottles) via Flatpak if you don't already have it
2. Open a terminal and git clone this package:
    ```bash
    git clone https://github.com/virtual-meme-machine/sims-linux-bottle.git ~/sims-linux-bottle
   ```
3. Run the script and provide it with the path to your game data zip:
    ```bash
    ~/sims-linux-bottle/src/main.py ~/Downloads/sims.zip
    ```
4. Wait for installation to complete
5. Launch 'The Sims - Complete Collection' using the shortcut in your applications menu, or via Bottles

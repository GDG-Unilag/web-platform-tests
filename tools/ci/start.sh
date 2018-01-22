#!/bin/bash

export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

sudo sh -c 'echo "
127.0.0.1	web-platform.test
127.0.0.1	www.web-platform.test
127.0.0.1	www1.web-platform.test
127.0.0.1	www2.web-platform.test
127.0.0.1	xn--n8j6ds53lwwkrqhv28a.web-platform.test
127.0.0.1	xn--lve-6lad.web-platform.test
0.0.0.0	nonexistent-origin.web-platform.test" >> /etc/hosts'

cd web-platform-tests
git pull

# Install Chome unstable
deb_archive=google-chrome-unstable_current_amd64.deb
wget https://dl.google.com/linux/direct/$deb_archive

if sudo update-alternatives --list google-chrome; then
    sudo update-alternatives --remove-all google-chrome
fi

# Installation will fail in cases where the package has unmet dependencies.
# When this occurs, attempt to use the system package manager to fetch the
# required packages and retry.
if ! sudo dpkg --install $deb_archive; then
    sudo apt-get -y install --fix-broken
    sudo dpkg --install $deb_archive
fi

if [ "$1" == "--shell" ]; then
    /bin/bash --login
fi

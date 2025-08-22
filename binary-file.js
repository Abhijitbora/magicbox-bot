# Create a bin directory in your home
mkdir -p ~/bin

# Download ffmpeg static build (example - check for latest version)
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Extract
tar xvf ffmpeg-release-amd64-static.tar.xz

# Move to your bin directory
mv ffmpeg-*-amd64-static/ffmpeg ~/bin/
mv ffmpeg-*-amd64-static/ffprobe ~/bin/

# Add to PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
ffmpeg -version

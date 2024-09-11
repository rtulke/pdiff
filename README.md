# pdiff

Perceptual Diff `pdiff` is a fast image comparison utility that makes use of a computational model of the human visual system to compare two images.

![Example](/demo/pdiff_table.png)


## Features

 - Comparison of several images
 - Comparison of two specific images
 - Support for various image formats (JPG, PNG, BMP, GIF, TIFF, WEBP, PPM)
 - Display of the percentage deviation
 - Filtering of similar images (5% or less difference)
 - Table output of the results
    - Display of file size
    - Display of pixel size
    - Display of hash values (MD5, SHA256, etc.)
    - Display of the comparison time per image pair
    - Display of an ID column with consecutive numbering
- Generation of reports in HTML format for better visualization
- Export formats (HTML, CSV, JSON)
- Statistical output for comparisons (performance, number of comparisons, etc.)
- Support for various hash algorithms (MD5, SHA256, etc.)

<img src="https://github.com/rtulke/pdiff/demo/bignumbers.png" width="48">
![Example](/demo/bignumbers.png)


### Supported Output Reports Formats

- '.csv', '.json', '.html'

### Supported Images Formats

- '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ppm']

Extended, but can be changed in pdiff script

- '.PPM', 'pnm', '.ico', '.pdf', '.eps' '.IM', '.DIB', '.MPO', '.tga', '.pcx' ,'.xbm' '.xv'

### Supported Hash Algorithm

- 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'

Additional hash functions depending on the operating system and available OpenSSL libraries, the following hash functions may also be supported:

- 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'blake2b', 'blake2s', 'shake_128', 'shake_256'


## User-defined tolerance

The parameter -p or --percent specifies the percentage of maximum deviation allowed for the images to still be considered “identical”. The default value is 100, which means that any deviation counts as a difference. If you do not specify it with -p value.

The maximum difference (max_difference) is calculated using the specified percentage. The maximum Hamming distance for the average_hash is 64 (since the hash is 64 bits long). If, for example, -p 80 is specified, this means that a difference of up to 20% of the maximum value (i.e. up to 12.8) is still considered identical.

When comparing different images, I noticed that images that are very similar usually have a deviation of less than 5%. Therefore I added the parameter -s -simular which only outputs images which have a calculated deviation of 5%. You could also use -p5 to get the same result.

## Pre-Setup

### Setting up a development environment

Not absolutely necessary because you can also download the repo as tar.gz.

### Git installation

```
sudo apt install -y git
```

If you want to check in your changes for the pdiff project via git, you should also enter your name and e-mail address for git.

```
git config --global user.name "Your Name"
git config --global user.email "your@email-address.com"
```

## Setup pdiff

### Installation of the required Python3 modules

There are some modules that need to be installed additionally. The other modules used by pdiff should already have been set up by the Python installation.

```
pip3 install Image imagehash futures tabulate
```

```
mkdir -p ~/dev/
cd ~/dev/
git clone https://github.com/rtulke/pdiff.git
```

We have now downloaded pdiff and it is located in the ~/dev directory below your user directory. If you want to execute pdiff as a command, you should make the following adjustments. Otherwise you would always have to write `python3 pdiff.py <param> <arg>.`


```
mkdir -p ~/bin/
cd ~/dev/pdiff
cp pdiff.py ~/bin/pdiff
chmod +x ~/bin/pdiff
```

To make the path known as a user in your system, you can do this either by editing the file `~/.profile` or the file `~/.bashrc` and adding this to your existing path variable.

Use your favorite editor and edit one of the two files.

```
vim ~/.bashrc
```

Add the following content in a new line at the end of the file.

```
export PATH="$PATH:~/bin"
``` 
So that the whole thing is also loaded in the system, you should now load the previously selected file `~/.bashrc` or `~/.profile` again. We do this with `source ~/.bashrc` or `source ~/.profile`

```
source ~/.bashrc
```

Now you should be able to execute the command easily.

```
pdiff --help
``` 


## Usage

You can now use the script as follows.

### To compare an entire directory

Make sure that the images are located in the specified directory and that the image formats are also supported by pdiff. See supported images formats 

```
pdiff -i /path/to/directory -p 80
```

### For a direct comparison of two image files

```
pdfiff -i image1.jpg image2.png -p 98
```

### For a comparison of several images in a directory where only images that are as similar as possible are output.

```
pdfiff -i /path/to/image-directory -s
```

Without parameter -p wich means it is using the default value (100)

```
pdfiff -i image1.jpg image2.png 
```

or

```
pdfiff -i /path/to/image-directory 

```

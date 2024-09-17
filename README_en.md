# pdiff

Perceptual Diff `pdiff` is a fast image comparison utility that makes use of a computational model of the human visual system to compare two images.

![Example](/demo/pdiff_table.png)

Comparison of the visual perception of images

Perceptual Image Comparisons, refer to methods and techniques for evaluating differences between images based on human visual perception, rather than purely mathematical or pixel-based approaches. This type of comparison focuses on how people perceive differences between images and is 
particularly useful in areas such as image quality evaluation, image processing.

Perception-based hashes are a completely different concept to the usual cryptographic hash methods such as MD5 or SHA. With cryptographic hashes, a one-sided hash value is generated based on the input data. And due to the avalanche effect, the resulting hash changes completely if you change a single bit. For this reason, 2 images can only have the same cryptographic hash if they are exactly the same. This makes cryptographic hashing not a viable solution to this problem.

In contrast, a perceptual hash is an image input-based fingerprint that can be used to compare images by calculating the Hamming distance (which essentially means counting the number of distinct individual bits). There are different algorithms for hashing perceptual images, but they all use similar steps to generate the media fingerprint. The easiest one to explain is the Average Hash (also called aHash). Let's take the following image and see how it works.

**1. downsizing**

First, the image is reduced to 8x8 pixels. This is the fastest way to remove high frequencies and details. In this step, the original size and aspect ratio are ignored and always reduced to 8x8 so that we have 64 resulting pixels.

**2. reduce the color**

Since we now have 64 pixels with their respective RGB value, we reduce the color by converting the image to grayscale. This leaves 64 color values.

**3. calculate the average color**

This is quite self-explanatory: Calculate the average color based on the previous 64 values.

**4. calculate the hash value**

The final fingerprint is calculated based on whether a pixel is lighter or darker than the average grayscale value we just calculated. Do this for each pixel and you will get a 64-bit hash.

**5. Comparing images**

To detect duplicate or similar images, calculate the perceptual hashes for both images:

```
Original:  1100100101101001001111000001100000001000000000000000011100111111
Thumbnail: 1100100101101001001111000001100000001000000000000000011100111111
```

As you can see, both hashes are identical. But this doesn't mean that similar images will always create equal hashes! If we manipulate the original image, and add a watermark, we get these hashes:

```
Original:  1100100101101001001111000001100000001000000000000000011100111111
Watermark: 1100100101111001001111000001100000011000000010000000011100111111
```

As you can see, these hashes are very similar, but not equal. To compare these hashes, we count the number of different bits (Hamming distance), which is 3 in this case. The higher this distance, the lower the change of identical or similar images.

**6. Other implementations**

The Average Hash implementation is the easiest and the fastest one, but it appears to be a bit too inaccurate and generates some false positives. Two other implementations are Difference Hash (or dHash) and pHash. Difference Hash follows the same steps as the Average Hash, but generates the fingerprint based on whether the left pixel is brighter than the right one, instead of using a single average value. 

Compared to Average Hash it generates less false positives, which makes it a great default implementation. pHash is an implementation that is quite different from the other ones, and does some really fancy stuff to increase the accuracy. It resizes to a 32x32 image, gets the Luma (brightness) value of each pixel and applies a discrete cosine transform (DCT) on the matrix. 

It then takes the top-left 8x8 pixels, which represent the lowest frequencies in the picture, to calculate the resulting hash by comparing each pixel to the median value. Because of it's complexity it is also the slowest one.

## Possible areas of application for Perceptual Diff

### Image and Video Compression
Can be used to assess the effects of various compression techniques on visual quality.
Algorithms like SSIM help ensure that compressed images or videos remain visually acceptable to the human eye.

### Quality Assurance in Digital Image Processing
Editing processes can be reviewed to ensure they do not generate unwanted visual artifacts.

### Medical Imaging
Can help maintain the quality of medical images after compression or transmission, ensuring that critical information is preserved.

### Image and Video Surveillance
Can be used to assess the effectiveness of video surveillance systems, especially after compression or in poor lighting conditions.

### Benchmarking of Image Processing Algorithms
Provides a way to benchmark algorithms based on perceived image quality rather than relying solely on numerical performance indicators.

### Scientific Research
Can be used to conduct experiments aimed at determining perception thresholds and other aspects of visual processing.

### E-Commerce and Online Marketing
Can also be used to ensure that images on a website still achieve the desired effect after compression, without losing important details.

### Automated Image Enhancement
Used to determine which improvements actually lead to a perceptible enhancement in image quality.

### Social Media and Image/Video Databases
Used, for example, to identify people (OSINT).
It is also employed to detect criminal content, such as pornography or illegal items (weapons, drugs, etc.).
Blocked images, e.g., for copyright infringement, can be identified.
Reduction of storage space within a database by recognizing already existing images.


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

## 160.000

With pdiff, up to 160,000 image pairs can be compared in one hour.

Tested with:
- 4 GB RAM
- 2x vCPU (Apple ARM M3)
- Debian GNU/Linux v12


## Supported Formats

### Report Formats

- '.csv', '.json', '.html'

#### HTML Report
![HTML_Report](/demo/html_report.png)


#### JSON Report
![JSON Report](/demo/json_report.png)

#### CSV Report
![CSV Report](/demo/csv_report.png)



### Images Formats

- '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ppm']

Extended, but can be changed in pdiff script

- '.PPM', 'pnm', '.ico', '.pdf', '.eps' '.IM', '.DIB', '.MPO', '.tga', '.pcx' ,'.xbm' '.xv'

### Hash Algorithm

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

usage: pdiff.py [-h] -i INPUT [INPUT ...] [-p PERCENT] [-s] [-o OUTPUT OUTPUT] [-T] [-t] [-N] [-H HASH] [-P] [-F] [-S]

Compare images in a directory or two specific image files using hashes.

options:
  -h, --help            show this help message and exit
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to a directory or to two image files
  -p PERCENT, --percent PERCENT
                        Percentage of maximum deviation that is considered identical (e.g., -p 80 means 20% deviation allowed)
  -s, --similar         Only print images with up to 5% difference
  -o OUTPUT OUTPUT, --output OUTPUT OUTPUT
                        Output format and file, e.g., "-o html output.html" or "-o csv output.csv" or "-o json output.json"
  -t, --table           Display comparison results as a text table
  -T, --time            Display comparison time for each image pair
  -N, --id              Add an ID column with a running number
  -H HASH, --hash HASH  Display hash for the specified algorithm (e.g., sha256, md5, etc.)
  -P, --pixel-size      Display image dimensions in pixels (width x height) in the table
  -F, --file-size       Display file size of images in the table
  -S, --stats           Display statistics: total time, average time per comparison, and number of comparisons

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

Try html a report, only similar images

```
pdiff -i static/ -s -o html index.html
```

Absolutely ALL

```
pdiff -i static/ -p90 -t -T -N -H md5 -P -F -S -o html index.html
```


# Script to download FaceScrub dataset

This project is released under a Creative Commons Attribution-NonCommercial 4.0 International Public License.
To view a copy of this license, visit <http://creativecommons.org/licenses/by-nc/4.0/legalcode>

**download_facescrub.py** downloads the [FaceScrub](http://vintage.winklerbros.net/facescrub.html) dataset described in 

> H.-W. Ng, S. Winkler.
> A data-driven approach to cleaning large face datasets.
> Proc. IEEE International Conference on Image Processing (ICIP), Paris, France, Oct. 27-30, 2014.

This code was tested on Ubuntu 14.04, Python 2.7.

# Requirements:

```bash
pip install requests

# Interchangeable with PIL. Can be ignored if you already have PIL installed
pip install Pillow

# Optional, but good to have, for robustly detecting file type.
# Might not work on Windows.
# In that case, simply ignore it.
pip install python-magic
```

# Steps to download FaceScrub dataset
1. First, obtain the FaceScrub files containing links to the images from <http://vintage.winklerbros.net/facescrub.html>
2. Next, set MY_USER_AGENT_STRING in the script. You can obtain it by visiting a site such as <https://www.whatismybrowser.com/detect/what-is-my-user-agent>
3. Finally, run download_facescrub.py to download the dataset.

# Example to download actors images.

Note: actors_users_normal_bbox.txt is obtained from the above link.

```bash
# To download and save full size images only
python download_facescrub.py actors_users_normal_bbox.txt actors/

# To download and save full size images along with cropped faces
python download_facescrub.py actors_users_normal_bbox.txt actors/ --crop_face

# Additional (optional) arguments to set log file name and time out to 10 seconds
python download_facescrub.py actors_users_normal_bbox.txt actors/ \
--crop_face --logfile=download.log --timeout=10
```

The above code will save full size images to the directory actors/images and faces (if required) to actors/faces



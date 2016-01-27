# FaceScrub face dataset

This project is released under a Creative Commons Attribution-NonCommercial 4.0 International Public License.
To view a copy of this license, visit <http://creativecommons.org/licenses/by-nc/4.0/legalcode>

**python\<version number\>\_download_facescrub.py** downloads the [FaceScrub](http://vintage.winklerbros.net/facescrub.html) dataset described in 

> H.-W. Ng, S. Winkler.
> A data-driven approach to cleaning large face datasets.
> Proc. IEEE International Conference on Image Processing (ICIP), Paris, France, Oct. 27-30, 2014.

If you are using Python 2, use the script `python2_download_facescrub.py`.
If you are using Python 3, use `python3_download_facescrub.py`.

This code was tested on Ubuntu 14.04 and Mac OS X El Capitan.

# Requirements:

* requests

```bash
pip install requests

```

If your Python version is < 2.7.9,
install requests security package extras to suppress "InsecurePlatformWarning".
```bash
pip install "requests[security]"
```

If your python installation is **Anaconda**, you may need to `conda install cryptography` before you `pip install "requests[security]"`
See [this Stackoverflow post](http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package?lq=1) for details.

If the above `requests[security]` installation fails, you might need to install additional packages on your system.
Consult this [link](http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package) for instructions.
More details on this issue can be found in this [Stackoverflow post](http://stackoverflow.com/questions/29134512/insecureplatformwarning-a-true-sslcontext-object-is-not-available-this-prevent)
and [urllib3 documentation](https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl).

* PIL

```bash
# Interchangeable with PIL. Can be ignored if you already have PIL installed
pip install Pillow
```

* python-magic (optional)

```bash
# Optional, but good to have, for robustly detecting file type.
# Might be difficult to get working on Windows. In that case, ignore it.
# If a file's type cannot be determined, it will be removed.
pip install python-magic
```

# Steps to download FaceScrub dataset
1. First, obtain the FaceScrub files containing links to the images from <http://vintage.winklerbros.net/facescrub.html>
2. Next, set MY_USER_AGENT_STRING in the script. You can obtain it by visiting a site such as <https://www.whatismybrowser.com/detect/what-is-my-user-agent>
3. Finally, run download_facescrub.py to download the dataset.

# Example to download actors images.

Note: actors_users_normal_bbox.txt is obtained from <http://vintage.winklerbros.net/facescrub.html>.

```bash
# In the following code, <version number> is "2" if you use Python 2, and "3" if you use Python 3.

# To download and save full size images only
python python<version number>_download_facescrub.py actors_users_normal_bbox.txt actors/

# To download and save full size images along with cropped faces
python python<version number>_download_facescrub.py actors_users_normal_bbox.txt actors/ --crop_face

# Additional (optional) arguments to set log file name, time out (10 seconds),
# max retries (3), start download at line 10 (note: line 1 is header) and
# end at line 20. Leave out --end_at_line to download till the end of file.
python python<version number>_download_facescrub.py actors_users_normal_bbox.txt actors/ \
--crop_face --logfile=download.log --timeout=10 --max_retries=3 --start_at_line=10 --end_at_line=20

```

The above code will save full size images to the directory actors/images and faces (if required) to actors/faces.

The naming convention for full size images is ``<name>_<image_id>.<ext>`` and ``<name>_<image_id>_<face_id>.<ext>`` for face images.
Note that `<ext>` is the extension of image format for the image. It need not be "jpeg".

All error messages in the log are of the form "Line \<number\>: \<error message\>: \<url\>", in case users are interested in them.

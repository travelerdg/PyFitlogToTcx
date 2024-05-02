##############################################################################
# MIT License
#
# Copyright (c) 2024 Brad D. Parker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##############################################################################

##############################################################################
# This program will convert a SportTracks FITLOG file into individual Garmin
# TCX files, one per activity. 
#
# Author: Brad D. Parker
# Contact: bdparker@gmail.com
##############################################################################
import setuptools

import pyfitlogtotcx

setuptools.setup(
    name='PyFitlogToTcx',
    version=pyfitlogtotcx.__version__,
    description='This program converts a SportTracks FITLOG file to Garmin TCX',
    url='https://github.com/braddparker/PyFitlogToTcx',
    packages=['pyfitlogtotcx'],
    entry_points={
        'console_scripts': ['fitlog2tcx = pyfitlogtotcx.convert_fitlog_to_tcx:entry_point'],
    },
)
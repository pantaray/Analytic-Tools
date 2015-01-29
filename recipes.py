# recipes.py - Here are some convenience functions that are used often
# 
# Author: Stefan Fuertinger [stefan.fuertinger@mssm.edu]
# Created: June 25 2013
# Last modified: 2015-01-29 11:51:09

from __future__ import division
import sys
import re
import fnmatch
import os
from numpy.linalg import norm
import numpy as np
from texttable import Texttable
from datetime import datetime, timedelta
from scipy import ndimage

##########################################################################################
def find_contiguous_regions(condition):
    """
    Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index.
    See http://stackoverflow.com/questions/4494404/find-large-number-of-consecutive-values-fulfilling-condition-in-a-numpy-array
    """
    # Find the indicies of changes in "condition"
    d = np.diff(condition)
    idx, = d.nonzero() 

    # We need to start things after the change in "condition". Therefore, 
    # we'll shift the index by 1 to the right.
    idx += 1

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size] # Edit

    # Reshape the result into two columns
    idx.shape = (-1,2)
    return idx

##########################################################################################
def query_yes_no(question, default=None):
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".

    Notes:
    ------
    This is recipe no. 577058 from ActiveState written by Trent Mick

    See also:
    ---------
    .. http://code.activestate.com/recipes/577058/
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

##########################################################################################
def natural_sort(l): 
    """
    Sort a Python list l in a "natural" way

    From the documentation of sort_nat.m:

    "Natural order sorting sorts strings containing digits in a way such that
    the numerical value of the digits is taken into account.  It is
    especially useful for sorting file names containing index numbers with
    different numbers of digits.  Often, people will use leading zeros to get
    the right sort order, but with this function you don't have to do that."

    For instance, a usual glob will give you a file listing sorted in this way 

        ['Elm11', 'Elm12', 'Elm2', 'elm0', 'elm1', 'elm10', 'elm13', 'elm9']

    Calling natural_sort on that list results in 

        ['elm0', 'elm1', 'Elm2', 'elm9', 'elm10', 'Elm11', 'Elm12', 'elm13']

    Inputs:
    -------
    l : Python list 
        Python list of strings

    Returns:
    --------
    l_sort : Python list
        Lexicographically sorted version of the input list l

    Notes:
    ------
    This function does *not* do any error checking and assumes you know what you are doing!
    The code below was written by Mark Byers as part of a Stackoverflow submission, see
    .. http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort

    See also:
    ---------
    MATLAB File Exchange submission sort_nat.m, currently available at 
    .. http://www.mathworks.com/matlabcentral/fileexchange/10959-sortnat-natural-order-sort
    
    Coding Horror's note on natural sorting of file listings
    .. http://www.codinghorror.com/blog/2007/12/sorting-for-humans-natural-sort-order.html
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

##########################################################################################
def get_numlines(fname):
    """
    Get number of lines of a txt-file

    Inputs:
    -------
    fname : str
        Path to file to be read

    Returns:
    --------
    lineno : int
        Number of lines in the file

    Notes:
    ------
    This code was written by Mark Byers as part of a Stackoverflow submission, 
    see .. http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python

    See also:
    ---------
    None
    """

    # Check if input makes sense
    if type(fname).__name__ != "str":
        raise TypeError("Filename has to be a string!")

    # Cycle through lines of files and do nothing
    with open(fname) as f:
        for lineno, l in enumerate(f):
            pass

    return lineno + 1

##########################################################################################
def issym(A,tol=1e-9):
    """
    Check for symmetry of a 2d NumPy array A

    Inputs:
    -------
    A : square NumPy 2darray
        A presumably symmetric matrix
    tol : positive real scalar
        Tolerance for checking if (A - A.T) is sufficiently small

    Returns:
    --------
    is_sym : bool
        True if A satisfies
                |A - A.T| <= tol * |A|,
        where |.| denotes the Frobenius norm. Thus, if the above inequality 
        holds, A is approximately symmetric. 

    Notes:
    ------
    An absolute-value based comparison is readily provided by NumPy's isclose

    See also:
    ---------
    The following thread at MATLAB central
    .. http://www.mathworks.com/matlabcentral/newsreader/view_thread/252727
    """

    # Check if Frobenius norm of A - A.T is sufficiently small (respecting round-off errors)
    try:
        is_sym = (norm(A-A.T,ord='fro') <= tol*norm(A,ord='fro'))
    except:
        raise TypeError('Input argument has to be a square matrix and a scalar tol (optional)!')

    return is_sym

##########################################################################################
def myglob(flpath,spattern):
    """
    Return a glob-like list of paths matching a pathname pattern BUT support fancy shell syntax

    Parameters
    ----------
    flpath : str
        Path to search (to search current directory use `flpath=''` or `flpath='.'`
    spattern : str
        Pattern to search for in `flpath`

    Returns
    -------
    flist : list
        A Python list of all files found in `flpath` that match the input pattern `spattern`

    Examples
    --------
    List all png/PNG files in the folder `MyHolidayFun` found under `Documents`

    >> filelist = myglob('Documents/MyHolidayFun','*.[Pp][Nn][Gg]')
    >> print filelist
    >> ['Documents/MyHolidayFun/img1.PNG','Documents/MyHolidayFun/img1.png']
        
    Notes
    -----
    None

    See also
    --------
    glob
    """

    # Sanity checks
    if type(flpath).__name__ != 'str':
        raise TypeError('Input has to be a string specifying a path!')
    if type(spattern).__name__ != 'str':
        raise TypeError('Pattern has to be a string!')

    # If user wants to search current directory, make sure that works as expected
    if (flpath == '') or (flpath.count(' ') == len(flpath)):
        flpath = '.'

    # Append trailing slash to filepath
    else:
        if flpath[-1] != os.sep: flpath = flpath + os.sep

    # Return glob-like list
    return [os.path.join(flpath, fnm) for fnm in fnmatch.filter(os.listdir(flpath),spattern)]

##########################################################################################
def printdata(data,leadrow,leadcol,fname=None):
    """
    Pretty-print/-save array-like data

    Parameters
    ----------
    data : NumPy 2darray
        An `M`-by-`N` array of data
    leadrow : Python list or NumPy 1darray
        List/array of length `M` providing labels to be printed in the first column of the table
        (strings/numerals or both)
    leadcol : Python list or NumPy 1darray
        List/array of length `N` or `N+1` providing labels to be printed in the first row of the table
        (strings/numerals or both). See Examples for details
    fname : string
        Name of a csv-file (with or without extension `.csv`) used to save the table 
        (WARNING: existing files will be overwritten!). Can also be a path + filename 
        (e.g., `fname='path/to/file.csv'`). By default output is not saved. 

    Returns
    -------
    Nothing : None

    Notes
    -----
    Uses the `texttable` module to print results

    Examples
    --------
    >>> import numpy as np
    >>> data = np.random.rand(2,3)
    >>> row1 = ["a","b",3]
    >>> col1 = np.arange(2)
    >>> printdata(data,row1,col1)
    +--------------------+--------------------+--------------------+--------------------+
    |                    |         a          |         b          |         3          |
    +====================+====================+====================+====================+
    | 0                  | 0.994018537964     | 0.707532139166     | 0.767497407803     |
    +--------------------+--------------------+--------------------+--------------------+
    | 1                  | 0.914193045048     | 0.758181936461     | 0.216752553325     |
    +--------------------+--------------------+--------------------+--------------------+
    >>> row1 = ["labels"] + row1
    >>> printdata(data,row1,col1,fname='dummy')
    +--------------------+--------------------+--------------------+--------------------+
    |       labels       |         a          |         b          |         3          |
    +====================+====================+====================+====================+
    | 0                  | 0.994018537964     | 0.707532139166     | 0.767497407803     |
    +--------------------+--------------------+--------------------+--------------------+
    | 1                  | 0.914193045048     | 0.758181936461     | 0.216752553325     |
    +--------------------+--------------------+--------------------+--------------------+
    >>> cat dummy.csv
    labels, a, b, 3
    0,0.994018537964,0.707532139166,0.767497407803
    1,0.914193045048,0.758181936461,0.216752553325

    See also
    --------
    texttable : a module for creating simple ASCII tables (currently available at the 
                `Python Package Index <https://pypi.python.org/pypi/texttable/0.8.1>`_)
    """

    # Sanity checks
    try:
        ds = data.shape
    except:
        raise TypeError('Input must be a M-by-N NumPy array, not ' + type(data).__name__+'!')
    if len(ds) > 2:
        raise ValueError('Input must be a M-by-N NumPy array!')

    try:
        m = len(leadcol)
    except: 
        raise TypeError('Input must be a Python list or NumPy 1d array, not '+type(leadcol).__name__+'!')
    try:
        n = len(leadrow)
    except: 
        raise TypeError('Input must be a Python list or NumPy 1d array, not '+type(leadrow).__name__+'!')

    if fname != None:
        if type(fname).__name__ != 'str':
            raise TypeError('Input fname has to be a string specifying an output filename, not '\
                            +type(fname).__name__+'!')
        if fname[-4::] != '.csv':
            fname = fname + '.csv'
        save = True
    else: save = False

    # Get dimension of data and corresponding leading column/row
    if len(ds) == 1: 
        K = ds[0]
        if K == m:
            N = 1; M = K
        elif K == n or K == (n-1):
            M = 1; N = K
        else: 
            raise ValueError('Number of elements in heading column/row and data don not match up!')
        data = data.reshape((M,N))
    else:
        M,N = ds

    if M != m:
        raise ValueError('Number of rows and no. of elements leading column do not match up!')
    elif N == n:
        head = [' '] + list(leadrow)
    elif N == (n-1):
        head = list(leadrow)
    else:
        raise ValueError('Number of columns and no. of elements in head row do not match up!')

    # Do something: create big data array including leading column
    Data = np.column_stack((leadcol,data.astype('str')))
    
    # Initialize table object and fill it with stuff
    table = Texttable()
    table.set_cols_align(["l"]*(N+1))
    table.set_cols_valign(["c"]*(N+1))
    table.set_cols_dtype(["t"]*(N+1))
    table.set_cols_width([18]*(N+1))
    table.add_rows([head],header=True)
    table.add_rows(Data.tolist(),header=False)
    
    # Pump out table
    print table.draw() + "\n"

    # If wanted, save stuff in a csv file
    if save:
        head = str(head)
        head = head.replace("[","")
        head = head.replace("]","")
        head = head.replace("'","")
        np.savetxt(fname,Data,delimiter=",",fmt="%s",header=head,comments="")

    return

##########################################################################################
def printstats(variables,pvals,group1,group2,g1str='group1',g2str='group2',verbose=True,fname=None):
    """
    Pretty-print previously computed statistical results 

    Parameters
    ----------
    variables : list or NumPy 1darray
        Python list/NumPy array of strings representing variables that have been tested
    pvals : Numpy 1darray
        Aray of `p`-values (floats) of the same size as `variables`
    group1 : NumPy 2darray
        An #samples-by-#variables array forming the "group1" set for the previously 
        computed statistical comparison
    group2 : NumPy 2darray
        An #samples-by-#variables array forming the "group2" set for the previously 
        computed statistical comparison
    g1str : string
        A string to be used in the generated table to highlight computed mean/std values of 
        the group1 dataset
    g2str : string
        A string to be used in the generated table to highlight computed mean/std values of 
        the group2 dataset
    fname : string
        Name of a csv-file (with or without extension `.csv`) used to save the table 
        (WARNING: existing files will be overwritten!). Can also be a path + filename 
        (e.g., `fname='path/to/file.csv'`). By default output is not saved. 

    Returns
    -------
    Nothing : None

    Notes
    -----
    Uses the `texttable` module to print results

    See also
    --------
    texttable : a module for creating simple ASCII tables (currently available at the 
                `Python Package Index <https://pypi.python.org/pypi/texttable/0.8.1>`_)
    printdata : a function that pretty-prints/-saves data given in an array (part of 
                `nws_tools.py <http://research.mssm.edu/simonyanlab/analytical-tools/nws_tools.printdata.html#nws_tools.printdata>`_
    """

    # Make sure that the groups, p-values and tested variables have appropriate dimensions
    try:
        m = len(variables)
    except: 
        raise TypeError('Input variables must be a Python list or NumPy 1d array of strings, not '+\
                        type(variables).__name__+'!')
    for var in variables:
        if str(var) != var:
            raise TypeError('All variables must be strings!')
    try: 
        M = pvals.size
    except: 
        raise TypeError('The p-values must be provided as NumPy 1d array, not '+type(variables).__name__+'!')
    if M != m:
        raise ValueError('No. of variables (=labels) and p-values do not match up!')
    try:
        N,M = group1.shape
    except: 
        raise TypeError('Dataset 1 must be a NumPy 2d array, not '+type(group1).__name__+'!')
    if M != m:
        raise ValueError('No. of variables (=labels) and dimension of group1 do not match up!')
    try:
        N,M = group2.shape
    except: 
        raise TypeError('Dataset 2 must be a NumPy 2d array, not '+type(group2).__name__+'!')
    if M != m:
        raise ValueError('No. of variables (=labels) and dimension of group2 do not match up!')

    # If column labels were provided, make sure they are printable strings
    if str(g1str) != g1str:
        raise TypeError('The optional column label `g1str` has to be a string!')
    if str(g2str) != g2str:
        raise TypeError('The optional column label `g2str` has to be a string!')

    # See if we're supposed to print stuff to the terminal or just save everything to a csv file
    msg = 'The optional switch verbose has to be True or False!'
    try:
        bad = (verbose == True or verbose == False)
    except: raise TypeError(msg)
    if bad == False:
        raise TypeError(msg)

    # If a filename was provided make sure it's a string 
    # (unicode chars in filenames are probably a bad idea...)
    if fname != None:
        if str(fname) != fname:
            raise TypeError('Input fname has to be a string specifying an output filename, not '\
                            +type(fname).__name__+'!')
        if fname[-4::] != '.csv':
            fname = fname + '.csv'
        save = True
    else: save = False

    # Construct table head
    head = [" ","p","mean("+g1str+")"," ","std("+g1str+")","</>",\
            "mean("+g2str+")"," ","std("+g2str+")"]

    # Compute mean/std of input data
    g1mean = group1.mean(axis=0)
    g1std  = group1.std(axis=0)
    g2mean = group2.mean(axis=0)
    g2std  = group2.std(axis=0)

    # Put "<" if mean(base) < mean(test) and vice versa
    gtlt = np.array(['<']*g1mean.size)
    gtlt[np.where(g1mean > g2mean)] = '>'

    # Prettify table
    pmstr = ["+/-"]*g1mean.size

    # Assemble data array
    Data = np.column_stack((variables,\
                            pvals.astype('str'),\
                            g1mean.astype('str'),\
                            pmstr,\
                            g1std.astype('str'),\
                            gtlt,\
                            g2mean.astype('str'),\
                            pmstr,\
                            g2std.astype('str')))

    # Construct texttable object
    table = Texttable()
    table.set_cols_align(["l","l","r","c","l","c","r","c","l"])
    table.set_cols_valign(["c"]*9)
    table.set_cols_dtype(["t"]*9)
    table.set_cols_width([12,18,18,3,18,3,18,3,18])
    table.add_rows([head],header=True)
    table.add_rows(Data.tolist(),header=False)
    table.set_deco(Texttable.HEADER)

    # Pump out table if wanted
    if verbose:
        print "Summary of statistics:\n"
        print table.draw() + "\n"

    # If wanted, save stuff in a csv file
    if save:
        head = str(head)
        head = head.replace("[","")
        head = head.replace("]","")
        head = head.replace("'","")
        np.savetxt(fname,Data,delimiter=",",fmt="%s",header=head,comments="")

##########################################################################################
def moveit(fname):
    """
    Check if a file exists, if yes, rename it

    Parameters
    ----------
    fname : str
        A string specifying (the path to) the file to be renamed (if existing)

    Returns
    -------
    Nothing : None

    See also
    --------
    None
    """

    # Check if input makes sense
    if type(fname).__name__ != "str":
        raise TypeError("Filename has to be a string!")

    # If file already exists, rename it
    if os.path.isfile(fname):
        newname = fname[:-3] + "_bak_"+\
                  str(datetime.now().year)+"_"+\
                  str(datetime.now().month)+"_"+\
                  str(datetime.now().day)+"_"+\
                  str(datetime.now().hour)+"_"+\
                  str(datetime.now().minute)+"_"+\
                  str(datetime.now().second)+\
                  fname[-3::]
        print "WARNING: File "+fname+" already exists, renaming it to: "+newname+"!"
        os.rename(fname,newname)

##########################################################################################
def regexfind(arr,expr):
    """
    Find regular expression in a NumPy array

    Parameters
    ----------
    arr : NumPy 1darray
        Array of strings to search 
    expr : str
        Regular expression to search for in the components of `arr`

    Returns
    -------
    ind : NumPy 1darray
        Index array of elements in `arr` that contain expression `expr`. If `expr` was not found
        anywhere in `arr` an empty array is returned

    Examples
    --------
    Suppose the array `arr` is given by

    >>> arr
    array(['L_a', 'L_b', 'R_a', 'R_b'], 
      dtype='|S3')

    If we want to find all elements of `arr` starting with `l_` or `L_` we could use

    >>> regexfind(arr,"[Ll]_*")
    array([0, 1])

    See also
    --------
    None
    """

    # Sanity checks
    try:
        arr = np.array(arr)
    except: raise TypeError("Input must be a NumPy array/Python list, not "+type(arr).__name__+"!")
    sha = arr.shape
    if len(sha) > 2 or (len(sha) == 2 and min(sha) != 1):
        raise ValueError("Input must be a NumPy 1darray or Python list!")

    if type(expr).__name__ != "str":
        raise TypeError("Input expression has to be a string, not "+type(expr).__name__+"!")

    # Now do something: start by compiling the input expression
    regex = re.compile(expr)

    # Create a generalized function to find matches
    match = np.vectorize(lambda x:bool(regex.match(x)))(arr)

    # Get matching indices and return
    return np.where(match == True)[0]

##########################################################################################
def MA(signal, window_size):
    """
    Smooth 1d/2darray using a moving average filter along one axis

    Parameters
    ----------
    signal : NumPy 1d/2darray
        Input signal of shape `M`-by-`N`, where `M` is the number of signal sources (regions, measuring
        devices, etc.) and `N` is the number of observations/measurements. Smoothing is performed along the 
        second axis, i.e., for each source all `N` observations are smoothed independently of each other
        using the same moving average window. 
    window_size : scalar
        Positive scalar defining the size of the window to average over

    Returns
    -------
    ma_signal : NumPy 1d/2darray
        Smoothed signal (same shape as input)

    See also
    --------
    None

    Notes
    -----
    None
    """

    # Sanity checks
    try:
        shs = signal.shape
    except: raise TypeError("Input `signal` must be a NumPy 2darray, not "+type(signal).__name__+"!")
    if len(shs) > 2:
        raise ValueError("Input `signal` must be a NumPy 2darray!")
    if np.sum(shs) <= 2:
        raise ValueError("Input `signal` is an array of only one element! ")
    if np.isnan(signal).max() == True or np.isinf(signal).max() == True or np.isreal(signal).min() == False:
        raise ValueError("Input `signal` must be real without NaNs or Infs!")

    try:
        bad = window_size <= 0
    except: raise TypeError("Input window-size must be a positive scalar!")
    if bad: raise ValueError("Input window-size must be a positive scalar!")
        
    # Assemble window and compute moving average of signal
    window = np.ones(int(window_size))/float(window_size)
    return ndimage.filters.convolve1d(signal,window,mode='nearest')

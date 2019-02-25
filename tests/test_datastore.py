# coding=utf-8
import hashlib
import os
import tempfile

import numpy as np

from dtscalibration import DataStore
from dtscalibration import open_datastore
from dtscalibration import read_sensornet_files
from dtscalibration import read_silixa_files

from dtscalibration.datastore_utils import shift_double_ended
from dtscalibration.datastore_utils import suggest_cable_shift_double_ended

np.random.seed(0)

fn = ["channel 1_20170921112245510.xml",
      "channel 1_20170921112746818.xml",
      "channel 1_20170921112746818.xml"]
fn_single = ["channel 2_20180504132202074.xml",
             "channel 2_20180504132232903.xml",
             "channel 2_20180504132303723.xml"]

if 1:
    # working dir is tests
    wd = os.path.dirname(os.path.abspath(__file__))
    data_dir_single_ended = os.path.join(wd, 'data', 'single_ended')
    data_dir_double_ended = os.path.join(wd, 'data', 'double_ended')
    data_dir_double_ended2 = os.path.join(wd, 'data', 'double_ended2')
    data_dir_silixa_long = os.path.join(wd,
                                        'data',
                                        'double_single_ended', 'channel_1')
    data_dir_sensornet_single_ended = os.path.join(wd,
                                                   'data',
                                                   'sensornet_oryx_v3.7')

else:
    # working dir is src
    data_dir_single_ended = os.path.join('..', '..',
                                         'tests', 'data', 'single_ended')
    data_dir_double_ended = os.path.join('..', '..',
                                         'tests', 'data', 'double_ended')
    data_dir_double_ended2 = os.path.join('..', '..',
                                          'tests', 'data', 'double_ended2')
    data_dir_silixa_long = os.path.join('..', '..',
                                        'tests',
                                        'data',
                                        'double_single_ended', 'channel_1')
    data_dir_sensornet_single_ended = os.path.join('..', '..',
                                                   'tests',
                                                   'data',
                                                   'sensornet_oryx_v3.7')


def test_read_data_from_single_file_double_ended():
    """
    Check if read data from file is correct
    :return:
    """
    fp0 = os.path.join(data_dir_double_ended, fn[0])
    data = read_data_from_fp_numpy(fp0)

    nx, ncols = data.shape

    err_msg = 'Not all points along the cable are read from file'
    np.testing.assert_equal(nx, 2330, err_msg=err_msg)

    err_msg = 'Not all columns are read from file'
    np.testing.assert_equal(ncols, 6, err_msg=err_msg)

    actual_hash = hashlib.sha1(data).hexdigest()
    desired_hash = '51b94dedd77c83c6cdd9dd132f379a39f742edae'

    assert actual_hash == desired_hash, 'The data is not read correctly'
    pass


def test_read_data_from_single_file_single_ended():
    """
    Check if read data from file is correct
    :return:
    """
    fp0 = os.path.join(data_dir_single_ended, fn_single[0])
    data = read_data_from_fp_numpy(fp0)

    nx, ncols = data.shape

    err_msg = 'Not all points along the cable are read from file'
    np.testing.assert_equal(nx, 1461, err_msg=err_msg)

    err_msg = 'Not all columns are read from file'
    np.testing.assert_equal(ncols, 4, err_msg=err_msg)

    actual_hash = hashlib.sha1(data).hexdigest()
    desired_hash = '58103e2d79f777f98bf279442eea138065883062'

    assert actual_hash == desired_hash, 'The data is not read correctly'
    pass


def test_empty_construction():
    ds = DataStore()
    assert ds._initialized, 'Empty obj in not initialized'
    pass


def test_repr():
    ds = DataStore()
    assert ds.__repr__().find('dtscalibration')
    assert ds.__repr__().find('Sections')
    pass


def test_has_sectionattr_upon_creation():
    ds = DataStore()
    assert hasattr(ds, '_sections')
    assert isinstance(ds._sections, str)
    pass


def test_sections_property():
    ds = DataStore({
        'st':                (['x', 'time'], np.ones((5, 5))),
        'ast':               (['x', 'time'], np.ones((5, 5))),
        'probe1Temperature': (['time'], range(5)),
        'probe2Temperature': (['time'], range(5))
        },
        coords={
            'x':    range(5),
            'time': range(5)})

    sections1 = {
        'probe1Temperature': [slice(7.5, 17.), slice(70., 80.)],  # cold bath
        'probe2Temperature': [slice(24., 34.), slice(85., 95.)],  # warm bath
        }
    sections2 = {
        'probe1Temperature': [slice(0., 17.), slice(70., 80.)],  # cold bath
        'probe2Temperature': [slice(24., 34.), slice(85., 95.)],  # warm bath
        }
    ds.sections = sections1

    assert isinstance(ds._sections, str)

    assert ds.sections == sections1
    assert ds.sections != sections2

    # delete property
    del ds.sections
    assert ds.sections is None

    pass


def test_io_sections_property():
    ds = DataStore({
        'st':                (['x', 'time'], np.ones((5, 5))),
        'ast':               (['x', 'time'], np.ones((5, 5))),
        'probe1Temperature': (['time'], range(5)),
        'probe2Temperature': (['time'], range(5))
        },
        coords={
            'x':    range(5),
            'time': range(5)})

    sections = {
        'probe1Temperature': [slice(7.5, 17.), slice(70., 80.)],  # cold bath
        'probe2Temperature': [slice(24., 34.), slice(85., 95.)],  # warm bath
        }

    ds.sections = sections

    # Create a temporary file to write data to.
    # 'with' method is used so the file is closed by tempfile
    # and free to be overwritten.
    with tempfile.NamedTemporaryFile('w') as tmp:
        temppath = tmp.name

    # Write the datastore to the temp file
    ds.to_netcdf(path=temppath)

    ds2 = open_datastore(temppath)

    assert ds.sections == ds2.sections

    # Close the datastore so the temp file can be removed
    ds2.close()
    ds2 = None

    # Remove the temp file once the test is done
    if os.path.exists(temppath):
        os.remove(temppath)

    pass


def test_read_silixa_files_single_ended():
    filepath = data_dir_single_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')

    assert ds._initialized

    pass


def test_read_silixa_files_double_ended():
    filepath = data_dir_double_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')

    assert ds._initialized

    pass


def test_read_silixa_files_lazy():
    filepath = data_dir_double_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml',
        load_in_memory='False')

    assert ds._initialized

    pass


def test_read_long_silixa_files():
    filepath = data_dir_silixa_long
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')

    assert ds._initialized

    pass


def test_read_sensornet_files_single_ended():
    filepath = data_dir_sensornet_single_ended
    ds = read_sensornet_files(
        directory=filepath,
        timezone_netcdf='UTC',
        timezone_input_files='UTC',
        file_ext='*.ddf')

    assert ds._initialized

    pass


def read_data_from_fp_numpy(fp):
    """
    Read the data from a single Silixa xml file. Using a simple approach

    Parameters
    ----------
    fp : file, str, or pathlib.Path
        File path

    Returns
    -------
    data : ndarray
        The data of the file as numpy array of shape (nx, ncols)

    Notes
    -----
    calculating i_first and i_last is fast compared to the rest
    """

    with open(fp) as fh:
        s = fh.readlines()

    s = [si.strip() for si in s]  # remove xml hierarchy spacing

    i_first = s.index('<data>')
    i_last = len(s) - s[::-1].index('</data>') - 1

    lssl = slice(i_first + 1, i_last, 3)  # list of strings slice

    data = np.loadtxt(s[lssl], delimiter=',', dtype=float)

    return data


def test_resample_datastore():
    filepath = data_dir_single_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')
    assert ds.time.size == 3

    ds_resampled = ds.resample_datastore(how='mean', time="47S")
    assert ds_resampled._initialized

    assert ds_resampled.time.size == 2

    pass


def test_timeseries_keys():
    filepath = data_dir_single_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')

    k = ds.timeseries_keys

    # no false positive
    for ki in k:
        assert ds[ki].dims == ('time',)

    # no false negatives
    k_not = [ki for ki in ds.data_vars if ki not in k]
    for kni in k_not:
        assert ds[kni].dims != ('time',)

    pass


def test_shift_double_ended_shift_backforward():
    # shifting it back and forward, should result in the same
    filepath = data_dir_double_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')

    dsmin1 = shift_double_ended(ds, -1)
    ds2 = shift_double_ended(dsmin1, 1)

    np.testing.assert_allclose(ds.x[1:-1], ds2.x)

    for k in ds2:
        if 'x' not in ds2[k].dims:
            continue

        old = ds[k].isel(x=slice(1, -1))
        new = ds2[k]

        np.testing.assert_allclose(old, new)

    pass


def test_suggest_cable_shift_double_ended():
    # need more measurements for proper testing. Therefore only checking if
    # no errors occur

    filepath = data_dir_double_ended
    ds = read_silixa_files(
        directory=filepath,
        timezone_netcdf='UTC',
        file_ext='*.xml')

    irange = np.arange(-4, 4)
    suggest_cable_shift_double_ended(ds, irange, plot_result=True)

    pass

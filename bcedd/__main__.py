#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __main__.py

# ----------------------------------------------
# import from standard lib
import logging
from urllib.parse import urlparse
import yaml
# import from other lib
# import from my project
import bcedd.setupcfg as setupcfg
import bcedd.xml4Erddap as x4edd

_type_list = ['table', 'grid']
_freq_list = ['weekly', 'monthly']


# ----------------------------------------------
def is_url(url_):
    """
    check if argument is an url

    :param url_: string of url to check

    :return: boolean
    """
    try:
        result = urlparse(url_)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _check_param(param_):
    """ """

    if not is_url(param_['url']):
        raise TypeError(f"invalid type for 'url'")

    if not isinstance(param_['type'], list):
        raise TypeError(f"'type' must be a list in yaml file")
    else:
        if any(tt not in _type_list for tt in param_['type']):
            raise ValueError(f"'type' value must be choose in {_type_list}")

    ff = param_['freq']
    if ff not in _freq_list:
        raise ValueError(f"'freq' value must be choose in _freq_list")


def main():
    """
    """
    # set up logger, paths, ...
    setupcfg.main()
    _logger = logging.getLogger(__name__)

    # read remote ERDDAP server yaml
    with open(setupcfg.eddyaml, 'r') as stream:
        try:
            data_loaded = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # select task to be done
    bindings = []
    for k, v in data_loaded.items():
        # check param
        try:
            _check_param(v)
        except Exception as err:
            raise Exception(f"Error in yaml file for {k}:\n\t{err}")

        # select frequency
        if v['freq'] == setupcfg.freq:
            # unpack type list
            for tt in v['type']:
                bindings += [(k,v['url'],tt)]

    for b in bindings:
        # run Generate
        x4edd.generate(*b)

    # aggregate
    dsxmlout = x4edd.concatenate()
    # check datasetid (select some, and remove duplicate)
    x4edd.check_datasetid(dsxmlout)
    # create hard link
    x4edd.replaceXmlBy(dsxmlout)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('Something goes wrong!!!')
        raise  # Throw exception again so calling code knows it happened

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

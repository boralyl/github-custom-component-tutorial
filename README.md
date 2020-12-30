# Github Custom for Home Assistant

[![](https://img.shields.io/github/license/boralyl/github-custom-component-tutorial?style=for-the-badge)](LICENSE)
[![](https://img.shields.io/github/workflow/status/boralyl/github-custom-component-tutorial/Python%20package?style=for-the-badge)](https://github.com/boralyl/github-custom-component-tutorial/actions)

## About

This repo contains a custom component for [Home Assistant](https://www.home-assistant.io) that was created in a tutorial series
on [aarongodfrey.dev](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/).

The tutorial walks through the steps to create a custom component for use in Home Assistant.

- [Part 1: Project Structure and Basics](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/)
- [Part 2: Unit Testing and Continuous Integration](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_2/)
- [Part 3: Adding a Config Flow](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_3/)
- [Part 4: Adding an Options Flow](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_4/)
- [Part 5: Debugging](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_5/)

## What It Is

An integration that monitors [GitHub](https://github.com/) repositories specified in a `configuration.yaml` file
or optionally via the Integrations UI.

## Running Tests

To run the test suite create a virtualenv (I recommend checking out [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for this) and install the test requirements.

```bash
$ pip install -r requirements.test.txt
```

After the test dependencies are installed you can simply invoke `pytest` to run
the test suite.

```bash
$ pytest
Test session starts (platform: linux, Python 3.7.5, pytest 5.4.3, pytest-sugar 0.9.4)
rootdir: /home/aaron/projects/github-custom, inifile: setup.cfg, testpaths: tests
plugins: forked-1.3.0, timeout-1.4.2, cov-2.10.1, aiohttp-0.3.0, requests-mock-1.8.0, xdist-2.1.0, sugar-0.9.4, test-groups-1.0.3, homeassistant-custom-component-0.0.20
collecting ...
 tests/test_config_flow.py ✓✓✓✓✓✓✓✓✓✓✓                                                                                                                                          85% ████████▌
 tests/test_sensor.py ✓✓                                                                                                                                                       100% ██████████

----------- coverage: platform linux, python 3.7.5-final-0 -----------
Name                                             Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------
custom_components/__init__.py                        0      0   100%
custom_components/github_custom/__init__.py         12      0   100%
custom_components/github_custom/config_flow.py      23      0   100%
custom_components/github_custom/const.py            18      0   100%
custom_components/github_custom/sensor.py           97      5    95%   86-89, 121
------------------------------------------------------------------------------
TOTAL                                              150      5    97%

Required test coverage of 93.0% reached. Total coverage: 96.67%

Results (0.73s):
      13 passed
```

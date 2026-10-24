# Github Custom for Home Assistant

[![](https://img.shields.io/github/license/boralyl/github-custom-component-tutorial?style=for-the-badge)](LICENSE)
[![](https://img.shields.io/github/actions/workflow/status/boralyl/github-custom-component-tutorial/pythonpackage.yaml?branch=main&style=for-the-badge)](https://github.com/boralyl/github-custom-component-tutorial/actions)

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

Requires Home Assistant 2024.11.0 or newer.

## Running Tests

The test suite requires Python 3.14, the version required by current releases of Home Assistant. Create a virtualenv
(I recommend checking out [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
for this) and install the test requirements.

```bash
$ pip install -r requirements.test.txt
```

After the test dependencies are installed you can simply invoke `pytest` to run
the test suite.

```bash
$ pytest
============================= test session starts ==============================
platform linux -- Python 3.14.8, pytest-9.0.3, pluggy-1.7.0
rootdir: /home/aaron/projects/github-custom-component-tutorial
configfile: setup.cfg
testpaths: tests
plugins: codspeed-5.0.3, aiohttp-1.1.1, homeassistant-custom-component-0.13.374, xdist-3.8.0, asyncio-1.4.0, cov-7.1.0, anyio-4.15.1, timeout-2.4.0, pytest_freezer-0.4.9, respx-0.23.1, github-actions-annotate-failures-0.4.2, picked-0.5.1, requests-mock-1.12.1, socket-0.8.1, unordered-0.8.0, syrupy-6.1.1
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 14 items

tests/test_config_flow.py ............                                   [ 85%]
tests/test_sensor.py ..                                                  [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.8-final-0 ________________

Name                                             Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------
custom_components/__init__.py                        0      0   100%
custom_components/github_custom/__init__.py         24      1    96%   36
custom_components/github_custom/config_flow.py      60     19    68%   49-50, 148-186
custom_components/github_custom/const.py            18      0   100%
custom_components/github_custom/sensor.py           99      5    95%   72, 86-89
------------------------------------------------------------------------------
TOTAL                                              201     25    88%
Required test coverage of 84.0% reached. Total coverage: 87.56%
============================== 14 passed in 0.41s ==============================
```

## Linting

Linting and formatting checks are run with [pre-commit](https://pre-commit.com/). To run them against the whole repo:

```bash
$ pre-commit run --all-files
```

To have them run automatically on every commit:

```bash
$ pre-commit install
```

# Corp Tools Doctrine Checker for AllianceAuth.<a name="aa-corptools-dc"></a>

![Release](https://img.shields.io/pypi/v/aa-corptools-dc?label=release)
![Licence](https://img.shields.io/github/license/geuthur/aa-corptools-dc)
![Python](https://img.shields.io/pypi/pyversions/aa-corptools-dc)
![Django](https://img.shields.io/pypi/frameworkversions/django/aa-corptools-dc.svg?label=django)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-corptools-dc/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-corptools-dc/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checks](https://github.com/Geuthur/aa-corptools-dc/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-corptools-dc/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-corptools-dc/graph/badge.svg?token=YfJSsDECUm)](https://codecov.io/gh/Geuthur/aa-corptools-dc)
[![Translation status](https://weblate.geuthur.de/widget/allianceauth/aa-corptools-doctrine-checker/svg-badge.svg)](https://weblate.geuthur.de/engage/allianceauth/)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

A Doctrine Checker Addon for Corp Tools

______________________________________________________________________

- [AA Corp Tools Doctrine Checker](#aa-corptools-dc)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Screenshots](#screenshots)
  - [Installation](#features)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add own Logger File](#step3)
    - [Step 4 - Migration to AA](#step4)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)
  - [Translations](#translations)
  - [Contributing](#contributing)

## Features<a name="features"></a>

- Corp Tools Doctrine Checker
  - Doctrine Overview
    - Check if Character met criteria for Doctrines
    - Ingame supported copy clipboard skill-queue
    - Copy Clipboard `missing` Skills
    - Search for specific Doctrine per Search Field
    - Filter by Category example: (Capital, Black OP Group, Mining)
    - Account Overview
    - Corporation Overview
  - Doctrine Administration
    - Simple Add Skill-Plans per Copy/Paste via Ingame Plans (copy to clipboard)
    - Language Localized Supported (Test Phase)
    - Doctrine Overview
    - Order-Weight

## Upcoming<a name="upcoming"></a>

- Detailed Modal-Overview for missing Skills
- Display min. req and recommended skill level
- Multi-Language Translation

## Screenshots<a name="screenshots"></a>

![Characters](https://raw.githubusercontent.com/geuthur/aa-corptools-dc/master/corptools_doctrine/images/characters.png "Characters")
![Missing](https://raw.githubusercontent.com/geuthur/aa-corptools-dc/master/corptools_doctrine/images/missing.png "Missing Skills")
![Doctrine](https://raw.githubusercontent.com/geuthur/aa-corptools-dc/master/corptools_doctrine/images/doctrine.png "Doctrine")
![Administration](https://raw.githubusercontent.com/geuthur/aa-corptools-dc/master/corptools_doctrine/images/admin.png "Administration")

## Installation<a name="installation"></a>

> [!NOTE]
> AA Corp Tools Doctrine Checker needs at least Alliance Auth v4.6.0
> Please make sure to update your Alliance Auth before you install this APP

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-corptools-dc
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

- Add `'corptools',` to `INSTALLED_APPS`
- Add `'corptools_doctrine',` to `INSTALLED_APPS`

### Step 3 - (Optional) Add own Logger File<a name="step3"></a>

To set up the Logger add following code to your `local.py`
Ensure that you have writing permission in logs folder.

```python
LOGGING["handlers"]["ct_doctrine_checker_file"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(BASE_DIR, "log/corptools_doctrine.log"),
    "formatter": "verbose",
    "maxBytes": 1024 * 1024 * 5,
    "backupCount": 5,
}
LOGGING["loggers"]["extensions.corptools_doctrine"] = {
    "handlers": ["ct_doctrine_checker_file", "console", "extension_file"],
    "level": "DEBUG",
}
```

### Step 4 - Migration to AA<a name="step4"></a>

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the AA Corp Tools Doctrine Checker

| ID                | Description                                                 |                                                        |
| :---------------- | :---------------------------------------------------------- | :----------------------------------------------------- |
| `basic_access`    | Can access the Corp Tools Doctrine Checker.                 | All Members with the Permission can access the MADC.   |
| `corp_access`     | Can view Characters from own Corporation.                   | Users with this can view all characters from own corp. |
| `alliance_access` | Can view Characters from own Alliance.                      | Users with this can view all characters from own ally. |
| `manage_access`   | Can manage this app, Corp Tools Doctrine Checker.           | Users with this permission can manage the MADC.        |
| `admin_access`    | Gives full access to this app, Corp Tools Doctrine Checker. | Users with this permission have full access.           |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

- AA_CORPTOOLS_DOCTRINE_APP_NAME: `"YOURNAME"` - Set the name of the APP

## Translations<a name="translations"></a>

[![Translations](https://weblate.geuthur.de/widget/allianceauth/aa-corptools-doctrine-checker/multi-auto.svg)](https://weblate.geuthur.de/engage/allianceauth/)

Help us translate this app into your language or improve existing translations. Join our team!"

## Contributing <a name="contributing"></a>

You want to improve the project?
Please ensure you read the [contribution guidelines](https://github.com/Geuthur/aa-corptools-dc/blob/master/CONTRIBUTING.md)

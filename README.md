# PHP Launchpad

Installer/Setip script for [PHP Launcher](https://github.com/hind-sagar-biswas/php_launcher) framework.

## Installation

There are 2 options available, you have **GUI application** (_currently for windows only_) and **CLI tool**. You can find both of them from [Releases](https://github.com/hind-sagar-biswas/php_launchpad/releases). Download whichever you prefer.

## CLI tool

The cli tool is caalled `php-launchpad`. You have to download the  `.rar` file for the cli from the binaries provided in releases. Extract it to desired location and add the location to `PATH`. Now you can access it from anywhere of your device

**Usage:** `php-launchpad [-h] [-v VERSION] [-l LOCATION] [-q] name`

CLI for taking arguments

```
positional arguments:
  name                  Project Name (compulsory)

options:
  -h, --help            show this help message and exit
  -v VERSION, --version VERSION
                        Version (optional)
  -l LOCATION, --location LOCATION
                        Location (optional)
  -q                    Flag q (optional) - initializes php_launcher project with default values on setup
```

### Creating new project

So let's say, we create a new `php_launcher` named **test_project** project in `/path/to/htdocs/` folder, then all we need to do is to:

```
cd /path/to/htdocs/
php-launchpad test_project
```

This will download the latest version of the `php_launcher`

#### To specify location:

```
php-launchpad test_project -l path/to/htdocs
```

### To specify version

```
php-launchpad test_project -v 0.1.1-beta
```

## GUI app

The GUI application is self guiding and easy to use where you have to specify project name, choose an install location and version, and with on click everything is done!

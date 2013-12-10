# Minnpost Hazmat

A look at HAZMAT accidents

## Data

Data compiled by [IRE](http://www.ire.org/nicar/database-library/databases/hazardous-materials/) and exported for MN only data.

### Notes

The `rpt_num` field is a unique identifier for an incident, but each incident can have more than one record, depending on how many different chemicals were spilled (one record for each substance).  Therefore, when counting incidents by various things, we mostly used `COUNT(DISTINCT rpt_num)`.

Only about 4 percent of incidents are considered "serious" (`HMIS_serious_inc_ind`), following these qualifications:
* A fatality or major injury caused by the release of a hazardous material
* the evacuation of 25 or more employees or responders or any number of the general public as a result of release of a hazardous material or exposure to fire
* a release or exposure to fire which results in the closure of a major transportation artery
* the alteration of an aircraft flight plan or operation
* the release of radioactive materials from Type B packaging
* the suspected release of a Risk Group 3 or 4 infectious substance
* the release of over 11.9 gallons or 88.2 pounds of a severe marine pollutant
* the release of a bulk quantity (over 119 gallons or 882 pounds) of a hazardous material.

## Data processing

1. The layout information originally recieved was not fully accurate or complete, so some minor updates were made and saved to `data/layour-cleaned.csv`.
1. To import the data into an SQLite database at `data/hazmat.db`, run the following: `python data-processing/import-sql.py`.
    * Note that this may take some time.
    * This is a destructive process and will remove data from the database.
1. Create JSON files of specific sets of data with: `python data-processing/questions.py`

## Development and running locally

### Prerequisites

All commands are assumed to on the [command line](http://en.wikipedia.org/wiki/Command-line_interface), often called the Terminal, unless otherwise noted.  The following will install technologies needed for the other steps and will only needed to be run once on your computer so there is a good chance you already have these technologies on your computer.

1. Install [Git](http://git-scm.com/).
   * On a Mac, install [Homebrew](http://brew.sh/), then do: `brew install git`
1. Install [NodeJS](http://nodejs.org/).
   * On a Mac, do: `brew install node`
1. Optionally, for development, install [Grunt](http://gruntjs.com/): `npm install -g grunt-cli`
1. Install [Bower](http://bower.io/): `npm install -g bower`
1. Install [Ruby](http://www.ruby-lang.org/en/downloads/), though it is probably already installed on your system.
1. Install [Bundler](http://gembundler.com/): `gem install bundler`
1. Install [Sass](http://sass-lang.com/): `gem install sass`
   * On a Mac do: `sudo gem install sass`
1. Install [Compass](http://compass-style.org/): `gem install compass`
   * On a Mac do: `sudo gem install compass`
1. Install [pip](https://pypi.python.org/pypi/pip): `easy_install pip`

### Get code and install packages

Get the code for this project and install the necessary dependency libraries and packages.

1. Check out this code with [Git](http://git-scm.com/): `git clone https://github.com/MinnPost/minnpost-hazmat.git`
1. Go into the template directory: `cd minnpost-hazmat`
1. Install NodeJS packages: `npm install`
1. Install Bower components: `bower install`
1. (optional) Use a [virtualenv](https://pypi.python.org/pypi/virtualenv).  If you don't use a `virtualenv`, you may have to use `sudo` to install Python packages.
1. Install Python packages: `pip install -r requirements.txt`

### Running

1. Run: `grunt server`
    * This will run a local webserver for development and you can view the application in your web browser at [http://localhost:8848](http://localhost:8848).
    * Utilize `index.html` for development, while `index-deploy.html` is used for the deployed version, and `index-build.html` is used to test the build before deployment.
    * The server runs `grunt watch` which will watch for linting JS files and compiling SASS.  If you have your own webserver, feel free to use that with just this command.

### Build

To build or compile all the assets together for easy and efficient deployment, do the following.  It will create all the files in the `dist/` folder.

1. Run: `grunt`

### Deploy

Deploying will push the relevant files up to Amazon's AWS S3 so that they can be easily referenced on the MinnPost site.  This is specific to MinnPost, and your deployment might be different.

1. Run: `grunt deploy`


## Hacks

*List any hacks used in this project, such as forked repos.  Link to pull request or repo and issue.*

resolver-api
==================================================

Fall 2014 USF Intern Project


Recommended Setup:
--------------------------------------------------

    pip install virtualenvwrapper

Put this in your .bashrc or .profile (whichever one actually loads):

    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/Devel
    export VIRTUALENVWRAPPER_SCRIPT=/usr/local/bin/virtualenvwrapper.sh
    source /usr/local/bin/virtualenvwrapper_lazy.sh

Start up a new bash window (or source your .bashrc):

    mkvirtualenv -a <path_to_project_root> <ve_name>

For me, that was `mkvirtualenv -a /User/kfunk/Repos/resolver-api/ resolver-api-ve`


Tests:
--------------------------------------------------

	nosetests --with-coverage --cover-erase --cover-package=resolverapi


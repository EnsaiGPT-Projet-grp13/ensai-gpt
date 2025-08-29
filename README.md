# Prerequisite:  PDM 
blabla

Install PDM for your user with pip 

`> pip install --user pdm`

Check your PDM version with 

`> pdm --version`

## In case of `pdm: command not found`

You must then add the PDM executable to your PATH environment 

To do so: 

Locate the folder in which pdm was installed with `pip list -v` (Usually `C:/Users/UserName/AppData/Roaming or Local/Python/Python310/site-packages`)

Find the `Scripts` folder which is a sibling of the `site-packages` (e.g. `C:/Users/UserName/AppData/Roaming or Local/Python/Python310/Scripts`; it should contain `pdm.exe`) and copy it. 

On Windows, search `Edit the system environment variables`

In `System Properties`, click `Environment variables` => One of the `User variables` should be named `Path`

`Edit` it and add the copied folder at the end of the variable, then save. 

You can now open a new terminal and retry 

# How to install the app 

`> pdm install`

That's all 😊

# How to run the app 

```> pdm start```

This starts a server accessible on `localhost:8000`

The API is then documented on `localhost:8000/docs`
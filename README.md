# Quick IT Management Tools

This is a set of lightweight IT management tools meant for small organizations and homelabs.  It is meant to fall somewhere between the capabilities of bash scripts and ansible.

The tools automate a handful of operations which I found myself having to repeatedly perform, but didn't have straightforward means of automation without jumping into much heavier and more complex solutions. The project is set up to provide a comfortable command line interface for manual and scripted use, while also being a fully usable Python 3 library.  

## Features

I add these features as I have need of them, but suggestions and contributions are welcome:

(All are in progress)

* Certificate checking and deployment
* Local hosts file management
* Local DNS static entry management
* Vyos wireguard management

## Debugging

```bash
pip install --editable .
```
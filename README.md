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

## Development Information

### Startup

From the command line, all persisted state is accessed through a singleton of the `Environment` class.  This is retrieved from the `Environment.default()` method.

During the first call to `Environment.default()` the environment is constructed. The configuration for the `Environment` object is provided by the `QuickConfig` class.  This in turn is constructed through the `QuickConfig.default()` static method, which attempts to load a configuration file from the default application configuration directory provided by `click`.

#### Object Construction

*These mechanisms are messy and need to be streamlined once I have a better idea of all the things they need to do.*

Objects which provide functionality are constructed dynamically at runtime from stored configuration. The `Environment` object has a field called `builders` which is a simple dataclass that has two `IBuilder` objects, one for building context objects, and one for building key stores.  

An `IBuilder` instantiates objects at the request of callers.  Types which the builder can produce must be registered using the `register` method, which takes the name The default implementation of an `IBuilder` is the `GenericBuilder` (these might be able to be squashed into one later). 

Registering a type with the builder involves giving it a friendly string name for the type (this is the human-readable name used in configuration files), the type of the object to be built, and the type of the configuration object. Types which are built by a builder must have a class initializer which accepts an instance of the configuration object as the first argument.

Configurations for objects are stored in the form of json/yaml dictionaries having three elements: (1) a string `name`, (2) a string `type` which matches a string type name registered with the appropriate builder, and (3) a `config` dictionary that will be passed into the initializer of the configuration object.  When something is going to be built, these three things are put into an `EntityConfig` object which then gets given to the builder's `build` method.  It will first instantiate the configuration type using *dacite*'s `from_dict` method on the `config` dictionary.  Then it will instantiate the final object by passing this configuration object into the initializer for that class.

All of this is basically a complicated way of managing dynamic configurations.

### Hosts

Hosts are one of the main entities. A host represents a computer or something that acts like a computer.  It has the following properties:

* A unique name
* A text description
* A list of client management mechanisms (ssh, api, etc)
* A set of type based configurations
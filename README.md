# appdaemon-blinds-control

As I startet with home automation one of the first things i wanted to automate was the blinds control.
Including the the blinds with home-assitant was easy (i used zwave controllers). I was instantly able to close an open the blinds via the web frintend. However my goal was the complete automated control thus i check how i could achieve that. I first tried ti use the buildin automation module. Automation was possible but is was not the right solution for me. I then search for a way to use normal python to code my automation and found appdaemon. Thus i wrote some appdaemon modules to control my blinds.

To make it easy for other here you can get my appdaemon modules. THe main features are:
* Blinds are automatically detected and an example configuration is created to include into your home-assistant configuration
* Each blind can be configured differently
* Blinds can be controlled accroding to sunset or based an defined time
* When using sunset/sunrise times, an earliest time to open blinds and a latest time to close blinds can be configured
* Blinds can be automaticly opened during night to cool down the house
* Presence detection can be used to disable automated blinds control if somebody is home

## Configuration
### appdaemon configuration
Just copy the file
* BlindsControl.py
to you apps folde rof appaemon and add the following configuration to your apps.yaml
`GlobalBlindsControl:
  module:                   BlindsControl
  class:                    GlobalBlindsControl
  debug:                    True

BlindsConfigConfiguration:
  module:                   BlindsControl
  class:                    BlindsControlConfiguration
  debug:                    True

BlindsControl:
 module:                    BlindsControl
 class:                     BlindsControl
 debug:                     True
`
### home-assistant configuration
If you use the generated configuration you can directly start using automated blinds control. The following files are created:
* config_blinds.yaml_
* input_boolean.yaml_
* input_datetime.yaml_
* input_number.yaml_

These files are generated on the first run of the module by appdaemon. You can create new configuration files lateron by using a switch in home-assistant.
The suffix _ is added by intention to prevent appdaemon to read the yaml files. The configuration files are generated in your apps folder of appdaemon. 

Just add all the generated configuration variables in
* input_boolean.yaml_
* input_datetime.yaml_
* input_number.yaml_

to your appropriate home-assistant configuration files.
The configuration file
* config_blinds_.yaml_

includes groups for each blinds with all the associated variables. Add these configuration file to your group configuration of home-assistant. A new group **config blinds** should be shown afterwards in you home-assisant instance provideing an blinds configuration for each of your blinds.
![config blinds group](https://github.com/foxcris/appdaemon-blinds-control/blob/development/images/config_blinds_group.PNG "config blinds group")
![blind configuration parameteters](https://github.com/foxcris/appdaemon-blinds-control/blob/development/images/config_blinds.PNG "blind configuration parameteters")

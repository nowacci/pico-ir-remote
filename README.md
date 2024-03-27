# pico-remote-ir

***

## Introduction
This is an example project of using an infrared transmitter to create wireless communication with a Raspberry Pi Pico receiving via an IR diode.


## How to install
1. Make sure that your Raspberry Pi Pico is connected to computer
2. Clone repository or Download ZIP and unpack 
    ```bash
    git clone https://github.com/nowacci/pico-ir-remote.git
    ```
   
    ```
    https://github.com/nowacci/pico-ir-remote/archive/refs/heads/master.zip
    ```
   
3. Using IDE (for example Thonny) move `/ir_rx`, `config.py` and `main.py` to your Raspberry Pi Pico
4. Done!


## Breadboard 
Here is list of components that you will need:

- Breadboard
- Raspberry Pi Pico
- 4 LEDs 
- 4 Resistors (I use 330Ω)
- IR diode
- NEC remote
- Wires
- USB Cable

Connect all components using scheme below:

![scheme](/img/breadboard.png)
<details>
  <summary>Show breadboard</summary>
   
![photo](/img/picture.jpg)
</details>

<details>
  <summary>Show remote</summary>
   
![photo](/img/remote.jpg)
</details>


## Functions
We have 3 modes of working as functions:
- `remote_value` - Default mode of code. By pressing 1-4 on remote you can turn on/off LEDs, 0 turns off all LEDs


- `default` - Mode that prints assign names of buttons on the remote control using by me



- `search` - Mode that prints vaules sent by remote control (good to detect new buttons/NEC remotes)



## Configuration
In this section I explain how to configure code to personal use

Open `main.py` file and go to callback function and choose mode by comment/uncomment code like below


```python
def callback(data, addr, ctrl):
    remote_value(data)   # default for this project
    #default(data)       # printing names of button on remote
    #search(data)        # searching for new values from other NEC remote  
```

```python
def callback(data, addr, ctrl):
    #remote_value(data)  # default for this project
    default(data)        # printing names of button on remote
    #search(data)        # searching for new values from other NEC remote  
```

```python
def callback(data, addr, ctrl):
    #remote_value(data)  # default for this project
    #default(data)       # printing names of button on remote
    search(data)         # searching for new values from other NEC remote  
```
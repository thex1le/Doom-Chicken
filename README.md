# Doom-Chicken
Round trip time network testing tool
usage: Doom_Chicken.py [-h] [-target_time TIME] [-check_time CHECK] -log_file
                       LOG [-ascii_off] (-dst DST | -file FILE)

          __//
        /.__.\
        \ \/ /
     '__/    \
      \-      )
       \_____/
    _____|_|____
         " "

usage: Doom_Chicken.py [-h] [-target_time TIME] [-check_time CHECK] -log_file
                       LOG [-ascii_off] (-dst DST | -file FILE)

Test Network speeds

optional arguments:
  -h, --help         show this help message and exit
  -target_time TIME  Time in sec between checks of the target
  -check_time CHECK  Time between checks to threads for updates on target
                     changes
  -log_file LOG      Filename to write the log file to
  -ascii_off         Disable the ascii to the terminal
  -dst DST           IP address to check
  -file FILE         List of IP targets in a file


Doom-Chicken is a Round trip time network testing tool, it supports targets of ip address, hostname or url of a web service.
Multiple targets can be loaded in a target file with the -file, one on each line.

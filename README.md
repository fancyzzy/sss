# SLA 2.4 Read Me



## What is SLA 2.4?

Site Log Analyzer(SLA) is a tool (GUI of python tkinter) designed for helping engineers to process and analyze  log files for easy debugging purpose. 

## Author

Felix.Zhang@nokia-sbell.com

## License

MIT

## Features

* Multi-thread Windows application 32/64 bit
* Automatically download log files
* Archives handling
* BSC real-time trace decoding
* Bunch of log keywords searching
* Result reporting

## Installation

bin\SLA2.4_Setup.exe

## Source Code

.

##  Python 3rd-Part Package Dependencies

1. tkdnd for drag & drop 

2. mttkinger for threads-safe

3. requests and exchangelib for email monitoring

   ​

## How to use

#### Configuration Files

1. The keywords.csv in the root directory is the log keyword database. Define your own product related words in it as the template showed.
2. The reserved_ftp.ini in the root directory is the ftp address used for SLA to automatically download log files when an log available indication contained in an outlook email.
3. The download_flag.txt in the root directory is the log available flag implicating an ftp address followed behind this flag. Update it for your own product team conventions 

#### Work-Flow

##### auto-download -> auto-analyze -> auto-report














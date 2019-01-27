{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf200
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww14460\viewh10820\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 Dependencies:\
\
To run this program, you must have the Chrome web browser installed on your computer, as well as a chrome driver.  \
Chrome is available here: https://www.google.com/chrome/\
the Chrome Driver File is available here: http://chromedriver.chromium.org/downloads\
Be sure to download the versions that are compatible with your computer/operating system.\
\
Once this program is initiated, you will be prompted to enter your amazon login credentials as well as the filepath to the chrome driver file you've downloaded.\
\
On mac computers, it'll look something like: /Users/johnsmith/Downloads/chromedriver\
On windows computers, it'll look something like: C:\\Users\\johnsmith\\Downloads\\chromedriver.exe\
\
This program will run for a while, depending on the quantity of your order history with Amazon.  After completion, two CSV files will be created in the directory this program was executed from, one containing all the raw order information data, another with a simple summary table.\
\
If you'd like to customize this program for your own usage, the cumulativeFrame variable contains all of the raw order information which can be used for any sort of analysis or visualization.}
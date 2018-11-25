# ClubSwipe
An automated card-swipe system for tracking attendance and payments in student organizations.

This application was originally developed for the Pitt Men's Glee Club but can easily be adapted for any student organization's needs.

## Hardware
ClubSwipe requires a usb magnetic stripe card swiper. It has been tested with [this one](https://www.amazon.com/gp/product/B01DVWQ2BO/ref=oh_aui_search_detailpage?ie=UTF8&psc=1).

## Requirements
ClubSwipe requires no additional packages beyond Python 3.x

## Usage
At this point, you may only run ClubSwipe as a python script. For example, with Python 3.x installed, one can run ClubSwipe with this line on terminal/command prompt:
```
python ClubSwipe.py
```
The script will automatically create a pickle file to hold its data and human-readable csv's on request, in the same directory where you run it.
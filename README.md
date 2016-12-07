# Open Print Stack

A full stack implementation of IPP/PWG printing.

Tired of shitty, Gb-sized, black-box printer drivers?
Why not go all the way back to the raw raster data and the single requests that
delivers it then!

If you have a modern, network connected printer, chances are it speaks Internet
Printing Protocol (IPP).
In fact, your printer might not actually know what to do with that PDF you're
trying to print, but it does understand PWG Raster files.
This project implements IPP and PWG, among other standards allowing you to have
near complete control over what you're asking your printer to print.


## How To Use

Note: the current iteration still relies on PkIPPLib, so step 0 is to get that.
And while you're at it, you'll also need PIL/PILLOW for anything to do with
raster.

Also note: lots of things are hard-coded at the moments, so you will have to
update those values appropriately, like setting the device IP in `print.py`.

Raster an image or document page to a format your printer understands, like PWG:

    ./raster.py encode ./test.png ./test.pwg

Send the raw raster file to your printer:

    ./print.py ./test.pwg


## Standards References

- [[PWG5102.4](https://ftp.pwg.org/pub/pwg/candidates/cs-ippraster10-20120420-5102.4.pdf)]
    PWG Raster Format

- [[RFC2565](https://tools.ietf.org/html/rfc2565)]
    Internet Printing Protocol/1.0: Encoding and Transport

- [[RFC2566](https://tools.ietf.org/html/rfc2566)]
    Internet Printing Protocol/1.0: Model and Semantics

- [[RFC2568](https://tools.ietf.org/html/rfc2568)]
    Rationale for the Structure of the Model and Protocol for the Internet
    Printing Protocol

- [[RFC2910](https://tools.ietf.org/html/rfc2910)]
    Internet Printing Protocol/1.1: Encoding and Transport

- [[RFC2911](https://tools.ietf.org/html/rfc2911)]
    Internet Printing Protocol/1.1: Model and Semantics

- [[RFC3380](https://tools.ietf.org/html/rfc3380)]
    Internet Printing Protocol (IPP): Job and Printer Set Operations

- [[RFC3381](https://tools.ietf.org/html/RFC3381)]
    Internet Printing Protocol (IPP): Job Progress Attributes

- [[RFC3382](https://tools.ietf.org/html/RFC3382)]
    Internet Printing Protocol (IPP): The 'collection' attribute syntax

- [[RFC3510](https://tools.ietf.org/html/RFC3510)]
    Internet Printing Protocol (IPP): IPP URL Scheme

- [[RFC1179](https://tools.ietf.org/html/rfc1179)]
    Line Printer Daemon Protocol


## Useful Commands

`ipptool` is a handy tool for talking IPP to known hosts, including probing the
capabilities of said host:

    ipptool -vt ipp://192.168.2.165/ get-printer-attributes.test

It's also possible to test for standard compliance:

    ipptool -t ipp://192.168.2.165/ ipp-2.2.test


## Glossary

- IPP : Internet Printing Protocol
- PWG : Printing Working Group
- LPD : Line Printer Daemon
- PPD : PostScript Printer Description
- PCL : Printer Control Language
- RIP : Raster Image Processor
- DNS-SD : DNS-based Service Discovery

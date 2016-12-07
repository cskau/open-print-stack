# open-print-stack

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


## Standards References

- [PWG5102-4] PWG Raster Format

    https://ftp.pwg.org/pub/pwg/candidates/cs-ippraster10-20120420-5102.4.pdf

- [RFC2565] Internet Printing Protocol/1.0: Encoding and Transport
    https://tools.ietf.org/html/rfc2565

- [RFC3380] Internet Printing Protocol (IPP): Job and Printer Set Operations
    https://tools.ietf.org/html/rfc3380

- [RFC2911] Internet Printing Protocol/1.1: Model and Semantics
    https://tools.ietf.org/html/rfc2911

- [RFC2568] Rationale for the Structure of the Model and Protocol for the
    Internet Printing Protocol
    https://tools.ietf.org/html/rfc2568

- [RFC2566] Internet Printing Protocol/1.0: Model and Semantics
    https://tools.ietf.org/html/rfc2566

- [RFC1179] Line Printer Daemon Protocol
    https://tools.ietf.org/html/rfc1179

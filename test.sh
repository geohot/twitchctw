#!/bin/bash -e
rm -f *.dec *.out
./ctw.py c enwik4
./ctw.py x enwik4
diff enwik4 enwik4.dec


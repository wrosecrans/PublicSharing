So, you have discovered the cool utility called rdfind from here:
http://rdfind.pauldreik.se/

It searches all the files in a path to see what the duplicates are, so you can find wasted space.
Unfortunately, it dumps the output into a fairly cryptic text format that isn't immediately very useful.
This python script takes the results text file from rdfind and processes it into a slightly more useful form.
Usage is simple:

will@will-desktop$ python rdproc.py ~/results.txt

And the output will be a bunch of lines like:

(181611400, 7264456, 25, '/home/will/.adobe/Flash_Player/NativeCache/95F4A94D2B37C2FC21D79C3B8417C1EE/689cb4c3/libadobecp-301806-1.so', 237035)

Which lists the total file size used, the size of each copy of the file, the number of copies of the file, a path to one of the copies, and the file ID in the results.txt file.
Total file size used is in bytes, and is just size * count.  Total space that could be recovered by having fewer copies would be (size * (count - 1)) sinc eyou would still want one hanging around.  The output of this python script is sorted with the biggest waste at the bottom.  Pipe it to tail to get just the worst offenders.  Use the file ID printed at the end of the line to grep for all the instances of the file in the results.txt.  (Just don't trivially automate that as a cleanup process because the file ID can also appear in the digits of the file size or something if you are just naively grepping.)

######################
#### WHAT IS THIS ####
######################

Hi! If you're reading this, you're probably either one of two groups of people. The first is the group of random people I'm throwing these files at. Hi! The second group is the one that sort of actually matters because you're probably a 15-112 staff! Hi, too!

This is, to put it simply, my (Yuto Takamoto's) 15-112 term project. This is an attempt to recreate an extremely popular Japanese indie game series, Touhou. Do note however that due to Python and Pygame's efficiency issues, there IS a HUGE limitation on how much I could actually do with this rendition. Even with pre-loading every sprite and multithreading several CPU-intensive portions of code, the program will still very noticeably lag on most computers. My personal desktop is a mid-high end gaming desktop from mid 2013. That said, while a 4.2ghz quad AMD A10-5800k is enough to run this sucker at (relatively) full FPS (60), most computers probably will not be able to.

#######################
### AKNOWLEDGEMENTS ###
#######################

Basically this entire project wouldn't be possible if it weren't for the absolutely fantastic lectures Professor Kosbie gives and all of the incredibly helpful review sessions/recitation/extra lectures/etc that the CA's help out with. So obviously my greatest gratitude goes out to you guys for making this course so ridiculously awesome!

That aside, 95% of the music and sprites used in this term project come straight from the Touhou Project games. They're simply rips from the game itself so credits to ZUN, the creator of this series.

Aside from that, I have borrowed two snippets of code from individuals on the internet. Proper credit has been given above the functions in main.py and sprites.py.

########################
##### INSTALLATION #####
########################

This code was written with python 2.7. Quick testing with py3 seems to suggest that this code will BREAK if 2.7 is not used.

The only dependancy that doesn't come with a default python installation is pygame. Please install that.

To run, simply run the main.py file and you should be good to go.
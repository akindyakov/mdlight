# Read me please

## Description
Web viewer for the bunch Markdown documents in directories.

I make almost all my notes in `.md` format and store it in git repo.

There are a lot of advantages, such as:

  * I can write it in [`vim`](https://en.wikipedia.org/wiki/Vim_(text_editor))
  * I can store it in [`git`](https://en.wikipedia.org/wiki/Git)
  * I can distribute it on all my computers (including my phone)
  * I can replicate it, just because it is `git`
  * I can insert pictures or something else in my notes

Arguing dialectically I should mention some disadvantages:

  * I am not able to show it to "normal" guys easily
  * I am not able to share it to other people by link
  * I am not able to see pictures in my notes, only links on it
  * I am not able to read it on my phone

Some of this problems I am tried to solve by mdlight.


## Requirements

To run:

  * python3
  * [pandoc](https://pandoc.org/)
  * [graphviz](https://en.wikipedia.org/wiki/Graphviz)

To test:

  * python3-pytest


## How to run
Run `./mdlight/server.py --help` and let see what happen. This is a entry point.


## How to test
Run `python3 -m pytest` cmd to execute all tests.

## To do

Some features I would like to make in future:

  * Support HTML pattern page and CSS style
  * I case of perfomance problems it would be helpful to use another web server (e.g. [werkzeug](http://werkzeug.pocoo.org/)) and cache.

# fxi

A kind of a "X11" command line applications building framework

![fxi](https://user-images.githubusercontent.com/8899756/40636004-4f8576f8-62d3-11e8-80fe-6a2304498a74.png)

Partly inspired by VisiData, partly from my own hatred for most of modern
in-browser applications, `fxi` has as its goal to facilitate to the
maximum building applications that you can interact with using your
keyboard and nothing more.

Actually, I don't want to open a web browser to check my e-mails, but
I don't want to read them at a white-in-black terminal screen, either.
I don't want to use AWS web console to check the state of SQS queues, but
I don't think awscli is too much of a better option. I want to read some
news and I want to see images.

`fxi` is going to help me with all that.

# Global Keybindings

- ctrl+c : Clear command line input.
- ctrl+d : "End of file": quit the program.
- ctrl+w : Closes currently open monitor.
- ctrl+r : "Reload": generally updates application data.
- ctrl+<1-9> : Change current tab.

# Global Commands

- :q : Quit the program.
- :c : Close current application.
- :r \<app_name\> : Reload current application.
- echo \<phrase\> : Print phrase into terminal.

# Special expressions:

- `!c` : The content of the clipboard.

# Applications embedded

It's not the idea to distribute applications "inside" fxi, but to allow
the user to download and use them on demand. But, right now, I'm simply
embedding them because it's much easier.

## Confluence

- Name: **confluence**
- Status: experimental
- Commands: ls, cd, v

Allows to navigate through Confluence spaces and pages.

## DuckDuckGo

- Name: **ddg**
- Status: experimental
- Commands: s (search)

Search the web using DuckDuckGo.

## Facebook

- Name: **fbook**
- Status: experimental
- Commands: ls, post

Post status updates into Facebook.

You'll need to have an Application token...

## IMDb

- Name: **imdb**
- Status: good enough
- Commands: s (search)

Search for movies and series on IMDb.

It displays title, rating, cover and cast.

## SQS

- Name: **sqs**
- Status: good enough
- Commands: mv, vm (view messages), purge

Lists Amazon SQS queues and allows you to move messages between them,
purge queues and view messages.

You AWS credentials files (`~/.aws/*`) must be properly set.

## Translate

- Name: **tlt**
- Status: good enough
- Commands: set \<from_lang\> \<to_lang\>, t (translate)

Translate phrases between idioms.

Uses `mymemory` as backend.

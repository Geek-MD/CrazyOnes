# Auror
Apple Updates Radical Outstanding Resource 

Auror is a software designed to automate notifications of Apple updates, using 2 services.

The first one uses GitHub Actions to scrape the content of the Apple updates website in the different languages ​​in which it is available.

The second one is a Python script which monitors the changes of the html files in this repository, and using a Telegram Bot notifies the user about new updates, ignoring the updates that have been notified previously.
